#!/usr/bin/env python3
"""Private, read-only ingestion and durable staging. No external action executor."""
from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
import hashlib
import fcntl
import imaplib
import json
import math
import os
from pathlib import Path
import re
import signal
import sqlite3
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parent
PRIVATE = ROOT / 'executive_v2_private'
STATES = ('READY', 'LEASED', 'RETRY', 'STAGED', 'BLOCKED', 'NEEDS_HUMAN')
KINDS = {
    'mail_review': ('MONEY', 'verify_origin_and_intent'),
    'commercial_correspondence': ('MONEY', 'verify_counterparty_and_actual_buyer_interest'),
    'receivable_notice': ('MONEY', 'verify_earned_receivable_and_bank_settlement'),
    'recruiter_correspondence': ('JOB', 'verify_employer_response_and_application_next_gate'),
    'questionnaire': ('JOB', 'verify_employer_then_supply_honest_data'),
    'verified_questionnaire': ('JOB', 'human_supply_honest_data'),
    'customer_positive': ('MONEY', 'connected_human_verify_and_respond'),
    'paid_invoice': ('MONEY', 'verify_net_new_bank_settlement'),
    'source_bounty': ('MONEY', 'verify_eligibility_payer_and_funding'),
}


def digest(value: bytes | str) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def require_hash(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('hash_required')
    return value


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    fd, name = tempfile.mkstemp(prefix='.heartbeat-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, sort_keys=True)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
        d = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(d)
        finally:
            os.close(d)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def dbopen(path=PRIVATE / 'state.sqlite3'):
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    # Create with private permissions before SQLite writes anything.
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    os.fchmod(fd, 0o600)
    os.close(fd)
    c = sqlite3.connect(path, timeout=15, isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    c.execute('PRAGMA journal_mode=WAL')
    c.execute('PRAGMA synchronous=FULL')
    c.executescript('''
    CREATE TABLE IF NOT EXISTS missions(lane TEXT PRIMARY KEY CHECK(lane IN ('MONEY','JOB')));
    INSERT OR IGNORE INTO missions VALUES('MONEY'),('JOB');
    CREATE TABLE IF NOT EXISTS evidence(hash TEXT PRIMARY KEY CHECK(length(hash)=64), created REAL NOT NULL);
    CREATE TRIGGER IF NOT EXISTS evidence_update BEFORE UPDATE ON evidence BEGIN SELECT RAISE(ABORT,'immutable'); END;
    CREATE TRIGGER IF NOT EXISTS evidence_delete BEFORE DELETE ON evidence BEGIN SELECT RAISE(ABORT,'immutable'); END;
    CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, fingerprint TEXT UNIQUE NOT NULL,
      evidence TEXT NOT NULL REFERENCES evidence(hash), classification TEXT NOT NULL, created REAL NOT NULL);
    CREATE TRIGGER IF NOT EXISTS event_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,'immutable'); END;
    CREATE TRIGGER IF NOT EXISTS event_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,'immutable'); END;
    CREATE TABLE IF NOT EXISTS work(id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES events(id),
      lane TEXT NOT NULL REFERENCES missions(lane), kind TEXT NOT NULL, gate TEXT NOT NULL,
      state TEXT NOT NULL CHECK(state IN ('READY','LEASED','RETRY','STAGED','BLOCKED','NEEDS_HUMAN')),
      created REAL NOT NULL, progressed REAL NOT NULL, deadline REAL, engaged INTEGER NOT NULL DEFAULT 0,
      attempts INTEGER NOT NULL DEFAULT 0, max_attempts INTEGER NOT NULL DEFAULT 3 CHECK(max_attempts BETWEEN 1 AND 10),
      next_attempt REAL NOT NULL DEFAULT 0, lease_until REAL, lease_token TEXT,
      UNIQUE(event_id,kind));
    CREATE TABLE IF NOT EXISTS attestations(work_id TEXT REFERENCES work(id),
      evidence TEXT REFERENCES evidence(hash), PRIMARY KEY(work_id,evidence));
    CREATE TRIGGER IF NOT EXISTS attestation_update BEFORE UPDATE ON attestations BEGIN SELECT RAISE(ABORT,'immutable'); END;
    CREATE TRIGGER IF NOT EXISTS attestation_delete BEFORE DELETE ON attestations BEGIN SELECT RAISE(ABORT,'immutable'); END;
    CREATE TABLE IF NOT EXISTS transitions(id INTEGER PRIMARY KEY, work_id TEXT REFERENCES work(id),
      old TEXT, new TEXT NOT NULL, at REAL NOT NULL, reason TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY, work_id TEXT REFERENCES work(id),
      number INTEGER NOT NULL, token TEXT UNIQUE NOT NULL, started REAL NOT NULL, ended REAL, result TEXT,
      UNIQUE(work_id,number));
    CREATE TABLE IF NOT EXISTS cursors(source TEXT PRIMARY KEY, validity TEXT NOT NULL,
      historical_end INTEGER NOT NULL, historical_uid INTEGER NOT NULL,
      fresh_uid INTEGER NOT NULL, fresh_end INTEGER NOT NULL DEFAULT 0,
      live_uid INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS metrics(id INTEGER PRIMARY KEY CHECK(id=1), last_cycle REAL,
      last_scan REAL, scanned INTEGER NOT NULL DEFAULT 0, last_error TEXT);
    INSERT OR IGNORE INTO metrics(id) VALUES(1);
    CREATE TABLE IF NOT EXISTS outcomes(event_id TEXT PRIMARY KEY REFERENCES events(id),
      lane TEXT NOT NULL REFERENCES missions(lane), kind TEXT NOT NULL,
      evidence TEXT NOT NULL REFERENCES evidence(hash), verified_at REAL NOT NULL);
    CREATE TRIGGER IF NOT EXISTS outcome_update BEFORE UPDATE ON outcomes BEGIN SELECT RAISE(ABORT,'immutable'); END;
    CREATE TRIGGER IF NOT EXISTS outcome_delete BEFORE DELETE ON outcomes BEGIN SELECT RAISE(ABORT,'immutable'); END;
    ''')
    # In-place migration of the initial v2 database; preserve past UIDs/events.
    columns = {r[1] for r in c.execute('PRAGMA table_info(cursors)')}
    if 'fresh_end' not in columns:
        c.execute('ALTER TABLE cursors ADD COLUMN fresh_end INTEGER NOT NULL DEFAULT 0')
    if 'live_uid' not in columns:
        c.execute('ALTER TABLE cursors ADD COLUMN live_uid INTEGER NOT NULL DEFAULT 0')
    for row in c.execute('SELECT * FROM cursors WHERE fresh_end=0 AND historical_end>0').fetchall():
        # Upgrade the already-scanned early-v2 snapshot without a skipped UID.
        oldend, scanned = int(row['historical_end']), int(row['historical_uid'])
        cutoff = max(0, oldend - 2000)
        recent_start = max(cutoff, scanned) if cutoff == 0 else cutoff
        c.execute('''UPDATE cursors SET historical_end=?,historical_uid=?,
              fresh_uid=?,fresh_end=?,live_uid=? WHERE source=?''',
              (cutoff, min(scanned,cutoff), recent_start, oldend, oldend, row['source']))
    return c


def begin(c):
    c.execute('BEGIN IMMEDIATE')


def transition(c, row, state, now, reason):
    c.execute('UPDATE work SET state=?,progressed=?,lease_until=NULL,lease_token=NULL WHERE id=?',
              (state, now, row['id']))
    c.execute('INSERT INTO transitions(work_id,old,new,at,reason) VALUES(?,?,?,?,?)',
              (row['id'], row['state'], state, now, reason))


def stage(c, *args, **kwargs):
    # A caller may include staging in the cursor transaction.
    owns_transaction = not c.in_transaction
    if owns_transaction:
        begin(c)
    try:
        result = _stage(c, *args, **kwargs)
        if owns_transaction:
            c.commit()
        return result
    except Exception:
        if owns_transaction:
            c.rollback()
        raise


def _stage(c, fingerprint, evidence_hash, kind='mail_review', *, now=None, deadline=None,
          engaged=False, independent_verification=None):
    """Local staging only. Verification is an explicit human attestation hash, never a header.

    Caller must independently verify that the attestation describes this event. This
    API stores a reference, not proof that the caller or the email is trustworthy.
    """
    now = time.time() if now is None else now
    if not isinstance(now, (int, float)) or not math.isfinite(now):
        raise ValueError('invalid_time')
    if deadline is not None and (not isinstance(deadline, (int, float)) or not math.isfinite(deadline)):
        raise ValueError('invalid_deadline')
    if not isinstance(engaged, bool):
        raise ValueError('invalid_engagement')
    require_hash(fingerprint)
    require_hash(evidence_hash)
    lane, gate = KINDS[kind]
    if kind in ('verified_questionnaire', 'customer_positive', 'paid_invoice'):
        require_hash(independent_verification)
    event_id = digest('event:' + fingerprint)
    work_id = digest(event_id + ':' + kind)
    c.execute('INSERT OR IGNORE INTO evidence VALUES(?,?)', (evidence_hash, now))
    c.execute('INSERT OR IGNORE INTO events VALUES(?,?,?,?,?)',
              (event_id, fingerprint, evidence_hash, kind, now))
    if independent_verification:
        require_hash(independent_verification)
        c.execute('INSERT OR IGNORE INTO evidence VALUES(?,?)', (independent_verification, now))
    state = 'BLOCKED' if kind == 'source_bounty' else 'NEEDS_HUMAN'
    result = c.execute('''INSERT OR IGNORE INTO work
      (id,event_id,lane,kind,gate,state,created,progressed,deadline,engaged)
      VALUES(?,?,?,?,?,?,?,?,?,?)''',
      (work_id, event_id, lane, kind, gate, state, now, now, deadline, bool(engaged)))
    if result.rowcount:
        c.execute('INSERT INTO transitions(work_id,old,new,at,reason) VALUES(?,NULL,?,?,?)',
                  (work_id, state, now, 'staged_not_executed'))
    if independent_verification:
        c.execute('INSERT OR IGNORE INTO attestations VALUES(?,?)', (work_id, independent_verification))
    return work_id


def release_for_local_review(c, work_id, now):
    """Explicit local scheduling only; cannot authorize external activity."""
    begin(c)
    try:
        row = c.execute('SELECT * FROM work WHERE id=?', (work_id,)).fetchone()
        if not row or row['state'] not in ('NEEDS_HUMAN', 'BLOCKED') or row['attempts'] >= row['max_attempts']:
            raise ValueError('not_releasable')
        transition(c, row, 'READY', now, 'local_review_requested')
        c.commit()
    except Exception:
        c.rollback()
        raise


def recover(c, now):
    # Called under the same writer transaction as claiming or maintenance.
    for row in c.execute("SELECT * FROM work WHERE state='LEASED' AND lease_until<=?", (now,)).fetchall():
        c.execute("UPDATE attempts SET ended=?,result='lease_expired' WHERE token=? AND ended IS NULL",
                  (now, row['lease_token']))
        retry(c, row, now, 'lease_expired')


def retry(c, row, now, reason):
    state = 'BLOCKED' if row['attempts'] >= row['max_attempts'] else 'RETRY'
    transition(c, row, state, now, reason)
    c.execute('UPDATE work SET next_attempt=? WHERE id=?',
              (now + min(3600, 30 * 2 ** max(0, row['attempts'] - 1)), row['id']))


def claim(c, lane, now, lease_seconds=60):
    if lane not in ('MONEY', 'JOB') or lease_seconds <= 0:
        raise ValueError('invalid_claim')
    begin(c)
    try:
        recover(c, now)
        row = c.execute('''SELECT * FROM work WHERE lane=? AND state IN ('READY','RETRY')
          AND next_attempt<=? AND attempts<max_attempts
          ORDER BY (kind IN ('questionnaire','verified_questionnaire') AND deadline<=?) DESC,
          engaged DESC, created ASC, id ASC LIMIT 1''', (lane, now, now)).fetchone()
        if row:
            token = uuid.uuid4().hex
            transition(c, row, 'LEASED', now, 'local_review_lease')
            c.execute('UPDATE work SET attempts=attempts+1,lease_until=?,lease_token=? WHERE id=?',
                      (now + lease_seconds, token, row['id']))
            c.execute('INSERT INTO attempts(work_id,number,token,started) VALUES(?,?,?,?)',
                      (row['id'], row['attempts'] + 1, token, now))
            row = dict(c.execute('SELECT * FROM work WHERE id=?', (row['id'],)).fetchone())
        c.commit()
        return row
    except Exception:
        c.rollback()
        raise


def finish(c, token, now, *, failed=False, dryrun=False):
    begin(c)
    try:
        row = c.execute("SELECT * FROM work WHERE lease_token=? AND state='LEASED' AND lease_until>?",
                        (token, now)).fetchone()
        if not row:
            raise ValueError('expired_or_unknown_lease')
        result = 'retryable_error' if failed else ('dryrun_not_executed' if dryrun else 'staged_not_executed')
        c.execute('UPDATE attempts SET ended=?,result=? WHERE token=?', (now, result, token))
        if failed:
            retry(c, row, now, result)
        else:
            transition(c, row, 'NEEDS_HUMAN' if dryrun else 'STAGED', now, result)
        c.commit()
    except Exception:
        c.rollback()
        raise


def record_outcome(c, work_id, evidence_hash, kind, verified_at):
    """Explicit external human verification import. Never called by scanner/dispatcher.

    MONEY means bank-available NEW NET funds; JOB means accepted paid work.
    Stripe balances, invoice status, source listings and proposals are not outcomes.
    No amounts, account identifiers or financial mutations are supported.
    """
    require_hash(evidence_hash)
    begin(c)
    try:
        row = c.execute('SELECT * FROM work WHERE id=?', (work_id,)).fetchone()
        expected = {'MONEY': 'bank_available_new_net_funds', 'JOB': 'accepted_paid_work'}
        if not row or kind != expected[row['lane']] or row['kind'] in ('source_bounty', 'mail_review', 'questionnaire'):
            raise ValueError('external_verification_required')
        c.execute('INSERT OR IGNORE INTO evidence VALUES(?,?)', (evidence_hash, verified_at))
        c.execute('INSERT OR IGNORE INTO outcomes VALUES(?,?,?,?,?)',
                  (row['event_id'], row['lane'], kind, evidence_hash, verified_at))
        c.commit()
    except Exception:
        c.rollback()
        raise


def classify(raw):
    """Conservative routing, NEVER evidence of identity, intent or payment.

    Unrelated messages do not become phantom MONEY tasks. Potentially relevant
    header hints enter a verification-only queue; no auto-email action exists.
    """
    try:
        msg = BytesParser(policy=policy.default).parsebytes(raw, headersonly=True)
        if msg.defects or not msg.get('From') or not msg.get('Subject'):
            return 'mail_review'
        subj = str(msg.get('Subject', '')).lower()
        if re.search(r'questionnaire|compl[eé]tez votre dossier|formulaire candidat|application questionnaire', subj):
            return 'questionnaire'
        if re.search(r'\b(candidature|application received|application status|recruiter|entretien|interview|screening|offer letter|assessment|poste)\b', subj):
            return 'recruiter_correspondence'
        if re.search(r'\b(facture|invoice|virement|paiement|payment received|payout|r[eè]glement|remittance)\b', subj):
            return 'receivable_notice'
        if re.search(r'\b(devis|prestations?|mission data|webanalytics|service proposal|commercial proposal|audit marketing|client inquiry|quote requested)\b', subj):
            return 'commercial_correspondence'
        return None
    except (ValueError, TypeError, LookupError):
        return 'mail_review'


def existing_credentials():
    """Reuse an owner-private existing Gmail App Password file without importing
    or executing any legacy SMTP module. No new credential is provisioned."""
    credential = Path.home() / 'job-acquisition-runtime/runtime/credentials/gmail_smtp.json'
    st = credential.stat()
    if st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise PermissionError('owner_private_credentials_required')
    data = json.loads(credential.read_text())
    username = str(data.get('email') or '').strip()
    password = str(data.get('app_password') or '').replace(' ', '')
    if username.count('@') != 1 or len(password) < 16:
        raise ValueError('invalid_credential_format')
    return username, password


def connect():
    username, password = existing_credentials()
    m = imaplib.IMAP4_SSL('imap.gmail.com', timeout=25)
    try:
        ok, _ = m.login(username, password)
        if ok != 'OK':
            raise RuntimeError('login_failed')
        return m
    except Exception:
        try:
            m.logout()
        except Exception:
            pass
        raise


def all_mail(m):
    ok, rows = m.list()
    if ok != 'OK':
        raise RuntimeError('list_failed')
    found = []
    for entry in rows or []:
        line, literal = entry if isinstance(entry, tuple) else (entry, None)
        if not isinstance(line, bytes):
            continue
        match = re.match(rb'^\(([^)]*)\)\s+(?:NIL|"(?:[^"\\]|\\.)*")\s+(.+)$', line)
        if not match or b'\\all' not in match[1].lower().split():
            continue
        name = match[2]
        if name.startswith(b'{'):
            if not isinstance(literal, bytes):
                raise RuntimeError('mailbox_literal_missing')
            name = literal
        elif name.startswith(b'"') and name.endswith(b'"'):
            name = re.sub(rb'\\(.)', rb'\1', name[1:-1])
        found.append(name)
    if len(found) != 1:
        raise RuntimeError('all_mail_not_unique')
    return b'"' + found[0].replace(b'\\', b'\\\\').replace(b'"', b'\\"') + b'"'


def response_number(m, name):
    _, values = m.response(name)
    if not values or not values[0] or not values[0].isdigit():
        raise RuntimeError('missing_mailbox_metadata')
    return int(values[0])


def scan_page(c, m, source, field, low, high, now):
    if low > high:
        return 0
    ok, rows = m.uid('search', None, 'UID', f'{low}:{high}')
    if ok != 'OK' or not rows or not isinstance(rows[0], bytes):
        raise RuntimeError('search_failed')
    uids = sorted(set(int(x) for x in rows[0].split()))
    if any(uid < low or uid > high for uid in uids):
        raise RuntimeError('uid_outside_window')
    begin(c)
    try:
        for uid in uids:
            ok, data = m.uid('fetch', str(uid), '(UID BODY.PEEK[HEADER])')
            if ok != 'OK':
                raise RuntimeError('fetch_failed')
            chunks = [x for x in data or [] if isinstance(x, tuple) and isinstance(x[1], bytes)]
            if len(chunks) != 1 or not re.search(rb'\bUID\s+' + str(uid).encode() + rb'\b', chunks[0][0]):
                raise RuntimeError('fetch_incomplete')
            raw = chunks[0][1]
            h = digest(raw)
            kind = classify(raw)
            if kind is not None:
                stage(c, digest('gmail-header:' + h), h, kind, now=now)
        # field is internal, never supplied by an external caller.
        if field not in ('fresh_uid', 'historical_uid', 'live_uid'):
            raise ValueError('invalid_cursor')
        c.execute(f'UPDATE cursors SET {field}=? WHERE source=?', (high, source))
        c.execute('UPDATE metrics SET scanned=scanned+? WHERE id=1', (len(uids),))
        c.commit()
        return len(uids)
    except Exception:
        c.rollback()
        raise


def scan(c, m, *, chunk=100, now=None):
    # Serialize scanners across processes, including mailbox resets and network IO.
    # flock is released by the kernel on crashes; queue writers remain independent.
    database = c.execute('PRAGMA database_list').fetchone()[2]
    fd = os.open(str(database) + '.scan.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _scan(c, m, chunk=chunk, now=now)
    finally:
        os.close(fd)


def _scan(c, m, *, chunk=100, now=None):
    """At most two bounded UID windows per cycle: fresh first, historical second.

    UID windows also bound sparse-mailbox work. Deleted UIDs may be skipped only
    after successful SEARCH. Every fetched event and its cursor commit together.
    """
    if not 1 <= chunk <= 500:
        raise ValueError('chunk_out_of_range')
    now = time.time() if now is None else now
    mailbox = all_mail(m)
    ok, _ = m.select(mailbox, readonly=True)
    if ok != 'OK':
        raise RuntimeError('select_failed')
    validity = str(response_number(m, 'UIDVALIDITY'))
    end = response_number(m, 'UIDNEXT') - 1
    source = digest(mailbox)
    row = c.execute('SELECT * FROM cursors WHERE source=?', (source,)).fetchone()
    if not row or row['validity'] != validity:
        # Recent messages must be processed promptly, not after years of backfill.
        # The older region is bounded separately and eventually fully scanned.
        cutoff = max(0, end - 2000)
        c.execute('''INSERT OR REPLACE INTO cursors
            (source, validity, historical_end, historical_uid, fresh_uid, fresh_end, live_uid)
            VALUES(?,?,?,?,?,?,?)''',
                  (source, validity, cutoff, 0, cutoff, end, end))
    row = c.execute('SELECT * FROM cursors WHERE source=?', (source,)).fetchone()
    # Newly arrived messages take absolute priority, even during deep history.
    count = scan_page(c, m, source, 'live_uid', row['live_uid'] + 1,
                      min(end, row['live_uid'] + chunk), now)
    # The snapshot's recent history is bounded; it cannot starve new mail.
    count += scan_page(c, m, source, 'fresh_uid', row['fresh_uid'] + 1,
                       min(row['fresh_end'], row['fresh_uid'] + chunk), now)
    count += scan_page(c, m, source, 'historical_uid', row['historical_uid'] + 1,
                       min(row['historical_end'], row['historical_uid'] + chunk), now)
    c.execute('UPDATE metrics SET last_scan=?,last_error=NULL WHERE id=1', (now,))
    return count


def summary(c, now=None, stale_after=900, stall_after=86400):
    now = time.time() if now is None else now
    metrics = dict(c.execute('SELECT * FROM metrics WHERE id=1').fetchone())
    stale = metrics['last_scan'] is None or now - metrics['last_scan'] > stale_after
    lanes = {}
    for lane in ('MONEY', 'JOB'):
        tasks = dict(c.execute('SELECT state,count(*) FROM work WHERE lane=? GROUP BY state', (lane,)))
        stalled = c.execute('SELECT count(*) FROM work WHERE lane=? AND progressed<?',
                            (lane, now - stall_after)).fetchone()[0]
        gate = c.execute('''SELECT gate FROM work WHERE lane=? AND state NOT IN ('BLOCKED','STAGED') ORDER BY
          (kind IN ('questionnaire','verified_questionnaire') AND deadline<=?) DESC,
          engaged DESC, created ASC, id ASC LIMIT 1''', (lane, now)).fetchone()
        last = c.execute('SELECT max(verified_at) FROM outcomes WHERE lane=?', (lane,)).fetchone()[0]
        lanes[lane] = {'tasks': tasks, 'stalled': stalled, 'last_new_externally_verified_outcome': last,
                       'next_gate': gate[0] if gate else 'await_verified_opportunity'}
    active_count = c.execute("SELECT count(*) FROM work WHERE state NOT IN ('BLOCKED','STAGED')").fetchone()[0]
    status = ('ERROR' if metrics['last_error'] else 'SCANNER_STALE' if stale else
              'STALLED' if any(v['stalled'] for v in lanes.values()) else
              'NEEDS_HUMAN' if active_count else 'IDLE_NO_ACTIVE_GATE')
    return {'at': now, 'status': status, 'scanner_stale': stale, 'last_cycle': metrics['last_cycle'],
            'last_scan': metrics['last_scan'], 'scanned': metrics['scanned'],
            'relevant': c.execute("SELECT count(*) FROM work WHERE kind!='mail_review'").fetchone()[0],
            'task_count': c.execute('SELECT count(*) FROM work').fetchone()[0],
            'actionable_review_count': active_count,
            'last_error': metrics['last_error'], 'missions': lanes, 'external_actions': 0,
            'bank_available_new_net_funds': 'UNKNOWN_UNLESS_EXTERNALLY_VERIFIED',
            'codex': 'disabled_no_proposals_executed'}


def cycle(c, *, connection_factory=connect, heartbeat=PRIVATE / 'heartbeat.json', now=None, chunk=100):
    now = time.time() if now is None else now
    m = None
    try:
        begin(c)
        recover(c, now)
        c.commit()
        m = connection_factory()
        scan(c, m, chunk=chunk, now=now)
    except Exception:
        c.rollback()
        # Exception strings and types can contain user-controlled/private data.
        c.execute("UPDATE metrics SET last_error='ingestion_or_recovery_failed' WHERE id=1")
    finally:
        if m is not None:
            try:
                m.logout()
            except Exception:
                c.execute("UPDATE metrics SET last_error='logout_failed' WHERE id=1")
    c.execute('UPDATE metrics SET last_cycle=? WHERE id=1', (now,))
    data = summary(c, now)
    atomic_json(heartbeat, data)
    return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('once', 'loop', 'status', 'test'))
    p.add_argument('--interval', type=int, default=300)
    p.add_argument('--chunk', type=int, default=100)
    args = p.parse_args()
    if args.mode == 'test':
        import unittest
        return int(not unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromName('test_executive_v2')).wasSuccessful())
    if not 1 <= args.chunk <= 500:
        p.error('--chunk must be between 1 and 500')
    c = dbopen()
    try:
        if args.mode == 'status':
            print(json.dumps(summary(c), sort_keys=True))
            return 0
        stopped = False
        def stop(*_):
            nonlocal stopped
            stopped = True
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        while not stopped:
            result = cycle(c, chunk=args.chunk)
            print(json.dumps(result, sort_keys=True), flush=True)
            if args.mode == 'once':
                return int(result['last_error'] is not None)
            until = time.monotonic() + max(30, args.interval)
            while not stopped and time.monotonic() < until:
                time.sleep(min(1, max(0, until - time.monotonic())))
    finally:
        c.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
