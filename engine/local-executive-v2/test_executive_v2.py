"""Pure tests and simulated integration: no credentials, network or financial systems."""
import json
import fcntl
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

import executive_v2 as x


def header(i=1, subject='Hello', extra=''):
    return f'From: untrusted@example.invalid\r\nSubject: {subject}\r\nMessage-ID: <{i}@invalid>\r\n{extra}\r\n'.encode()


class IMAP:
    def __init__(self, count=0):
        self.messages = {i: header(i) for i in range(1, count + 1)}
        self.validity = 1
        self.selected = None
        self.fetches = []
        self.fail = None
        self.closed = False

    def list(self):
        return 'OK', [b'(\\HasNoChildren) "/" "INBOX"',
                      b'(\\HasNoChildren \\All) "/" "[Gmail]/Tous les messages"']

    def select(self, mailbox, readonly=False):
        assert readonly is True
        self.selected = mailbox
        return 'OK', [str(len(self.messages)).encode()]

    def response(self, name):
        return name, [str(self.validity if name == 'UIDVALIDITY' else max(self.messages, default=0) + 1).encode()]

    def uid(self, command, *args):
        if command == 'search':
            if self.fail == 'search':
                return 'NO', []
            low, high = map(int, args[-1].split(':'))
            return 'OK', [b' '.join(str(i).encode() for i in sorted(self.messages) if low <= i <= high)]
        assert command == 'fetch'
        assert args[1] == '(UID BODY.PEEK[HEADER])'
        uid = int(args[0])
        self.fetches.append(uid)
        if self.fail == uid:
            raise OSError('secret address and bank number must never be logged')
        return 'OK', [(f'1 (UID {uid} BODY[HEADER] {{100}}'.encode(), self.messages[uid]), b')']

    def logout(self):
        self.closed = True


class V2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'private' / 'state.sqlite3'
        self.c = x.dbopen(self.path)
        self.addCleanup(lambda: self.c.close())

    def task(self, kind='mail_review', key='a', now=0, **kw):
        return x.stage(self.c, x.digest(key), x.digest('evidence' + key), kind, now=now, **kw)

    def row(self, key):
        return self.c.execute('SELECT * FROM work WHERE id=?', (key,)).fetchone()

    def ready(self, **kw):
        key = self.task(**kw)
        x.release_for_local_review(self.c, key, 1)
        return key

    def test_two_distinct_lanes(self):
        self.task('questionnaire')
        self.task('source_bounty', key='b')
        self.assertEqual({r[0] for r in self.c.execute('SELECT lane FROM work')}, {'MONEY', 'JOB'})
        self.assertEqual(self.c.execute('SELECT count(*) FROM missions').fetchone()[0], 2)

    def test_idempotency(self):
        self.assertEqual(self.task(), self.task())
        self.assertEqual(self.c.execute('SELECT count(*) FROM work').fetchone()[0], 1)
        self.assertEqual(self.c.execute('SELECT count(*) FROM transitions').fetchone()[0], 1)

    def test_evidence_immutable(self):
        self.task()
        for sql in ('UPDATE evidence SET created=2', 'DELETE FROM evidence'):
            with self.assertRaises(sqlite3.IntegrityError):
                self.c.execute(sql)

    def test_deadline_priority(self):
        self.ready(kind='questionnaire', key='old', now=0, engaged=True)
        urgent = self.ready(kind='verified_questionnaire', key='urgent', now=2, deadline=5,
                            independent_verification=x.digest('human evidence'))
        self.assertEqual(x.claim(self.c, 'JOB', 10)['id'], urgent)

    def test_old_engaged_priority(self):
        self.ready(key='new', now=20, engaged=True)
        old = self.ready(key='old', now=10, engaged=True)
        self.ready(key='unengaged', now=0)
        self.assertEqual(x.claim(self.c, 'MONEY', 30)['id'], old)

    def test_reboot_lease_recovery(self):
        key = self.ready()
        lease = x.claim(self.c, 'MONEY', 10, lease_seconds=5)
        self.c.close()
        self.c = x.dbopen(self.path)
        self.assertIsNone(x.claim(self.c, 'MONEY', 16))
        self.assertEqual(self.row(key)['state'], 'RETRY')
        with self.assertRaises(ValueError):
            x.finish(self.c, lease['lease_token'], 17)
        self.assertIsNotNone(x.claim(self.c, 'MONEY', 46))
        self.assertEqual(self.c.execute('SELECT result FROM attempts ORDER BY id').fetchone()[0], 'lease_expired')

    def test_retry_cap_and_backoff(self):
        key = self.ready()
        for now, delay in ((10, 30), (41, 60), (102, 120)):
            item = x.claim(self.c, 'MONEY', now)
            x.finish(self.c, item['lease_token'], now + 1, failed=True)
            self.assertEqual(self.row(key)['next_attempt'], now + 1 + delay)
            self.assertIsNone(x.claim(self.c, 'MONEY', now + 2))
        self.assertEqual(self.row(key)['state'], 'BLOCKED')
        self.assertIsNone(x.claim(self.c, 'MONEY', 10000))
        with self.assertRaises(ValueError):
            x.release_for_local_review(self.c, key, 10001)

    def test_concurrent_claim_exclusion(self):
        self.ready()
        other = x.dbopen(self.path)
        try:
            self.assertIsNotNone(x.claim(self.c, 'MONEY', 10))
            self.assertIsNone(x.claim(other, 'MONEY', 11))
        finally:
            other.close()

    def test_dryrun_not_done(self):
        key = self.ready()
        lease = x.claim(self.c, 'MONEY', 10)
        x.finish(self.c, lease['lease_token'], 11, dryrun=True)
        self.assertEqual(self.row(key)['state'], 'NEEDS_HUMAN')
        self.assertEqual(self.c.execute('SELECT count(*) FROM outcomes').fetchone()[0], 0)

    def test_emitted_task_only_staged(self):
        key = self.ready()
        lease = x.claim(self.c, 'MONEY', 10)
        x.finish(self.c, lease['lease_token'], 11)
        self.assertEqual(self.row(key)['state'], 'STAGED')
        self.assertEqual(x.summary(self.c, 12)['external_actions'], 0)

    def test_verified_dispatch(self):
        for kind, lane, gate in (
            ('verified_questionnaire', 'JOB', 'human_supply_honest_data'),
            ('customer_positive', 'MONEY', 'connected_human_verify_and_respond'),
            ('paid_invoice', 'MONEY', 'verify_net_new_bank_settlement')):
            with self.assertRaises(ValueError):
                self.task(kind, key=kind)
            key = self.task(kind, key=kind, independent_verification=x.digest('independent ' + kind))
            row = self.row(key)
            self.assertEqual((row['lane'], row['gate'], row['state']), (lane, gate, 'NEEDS_HUMAN'))

    def test_no_stripe_or_bounty_money_claims(self):
        bounty = self.task('source_bounty')
        paid = self.task('paid_invoice', key='invoice', independent_verification=x.digest('attestation'))
        for key, kind in ((bounty, 'bank_available_new_net_funds'), (paid, 'stripe_balance'), (paid, 'paid_invoice')):
            with self.assertRaises(ValueError):
                x.record_outcome(self.c, key, x.digest('external'), kind, 12)
        self.assertIsNone(x.summary(self.c, 20)['missions']['MONEY']['last_new_externally_verified_outcome'])

    def test_separate_explicit_outcome_evidence(self):
        key = self.task('verified_questionnaire', independent_verification=x.digest('verified'))
        x.record_outcome(self.c, key, x.digest('accepted paid work evidence'), 'accepted_paid_work', 10)
        summary = x.summary(self.c, 11)
        self.assertEqual(summary['missions']['JOB']['last_new_externally_verified_outcome'], 10)
        self.assertIsNone(summary['missions']['MONEY']['last_new_externally_verified_outcome'])

    def test_879_oldest_first_no_loss(self):
        m = IMAP(879)
        counts = [x.scan(self.c, m, chunk=100, now=i) for i in range(9)]
        self.assertEqual(counts, [100] * 8 + [79])
        self.assertEqual(m.fetches, list(range(1, 880)))
        self.assertEqual(self.c.execute('SELECT count(*) FROM work').fetchone()[0], 0)
        self.assertEqual(self.c.execute('SELECT scanned FROM metrics WHERE id=1').fetchone()[0], 879)
        self.assertEqual(x.scan(self.c, m, now=10), 0)


    def test_only_outcome_relevant_mail_enters_queues(self):
        m = IMAP(6)
        m.messages = {
            1: header(1, subject='Your subscription to the newsletter'),
            2: header(2, subject='Questionnaire candidat — Université'),
            3: header(3, subject='Re: Candidature — gestionnaire'),
            4: header(4, subject='Re: Mission Data Analyst — devis'),
            5: header(5, subject='Facture 004 — paiement effectué'),
            6: header(6, subject='Not interested, stop contacting us')
        }
        self.assertEqual(x.scan(self.c, m, chunk=10), 6)
        items = self.c.execute('SELECT lane,kind FROM work ORDER BY created,id').fetchall()
        kinds = {r['kind'] for r in items}
        self.assertEqual(kinds, {'questionnaire','recruiter_correspondence',
                                 'commercial_correspondence','receivable_notice'})
        self.assertEqual(len(items), 4)
        self.assertEqual(self.c.execute('SELECT scanned FROM metrics WHERE id=1').fetchone()[0], 6)
        self.assertEqual(self.c.execute('SELECT count(*) FROM outcomes').fetchone()[0], 0)

    def test_initial_priority_recent_while_deep_backfill(self):
        m = IMAP(5000)
        m.messages[4900] = header(4900,subject='Questionnaire candidat')
        x.scan(self.c,m,chunk=100)
        self.assertIn(3001,m.fetches)
        self.assertIn(1,m.fetches)
        self.assertNotIn(4900,m.fetches)
        for _ in range(19):
            x.scan(self.c,m,chunk=100)
        self.assertIn(4900,m.fetches)
        row=self.c.execute('SELECT * FROM cursors').fetchone()
        self.assertEqual(row['historical_end'],3000)
        self.assertEqual(row['fresh_end'],5000)
        self.assertEqual(row['live_uid'],5000)
        self.assertEqual(row['fresh_uid'],5000)

    def test_new_mail_jumps_ahead_of_existing_history(self):
        m=IMAP(5000)
        x.scan(self.c,m,chunk=100)
        m.messages[5001]=header(5001,subject='Questionnaire candidat')
        x.scan(self.c,m,chunk=100)
        self.assertEqual(m.fetches[200],5001)
        self.assertEqual(self.c.execute('SELECT count(*) FROM work WHERE lane="JOB"').fetchone()[0],1)


    def test_archived_in_all_mail(self):
        m = IMAP(1)  # exists only in All Mail; fake has no Inbox selection support
        x.scan(self.c, m)
        self.assertEqual(m.selected, b'"[Gmail]/Tous les messages"')
        self.assertEqual(len(m.fetches), 1)

    def test_empty_mailbox(self):
        self.assertEqual(x.scan(self.c, IMAP(), now=5), 0)
        self.assertFalse(x.summary(self.c, 6)['scanner_stale'])

    def test_fresh_mail_before_backfill(self):
        m = IMAP(879)
        x.scan(self.c, m, chunk=100)
        m.messages[880] = header(880)
        x.scan(self.c, m, chunk=100)
        self.assertEqual(m.fetches[100:103], [880, 101, 102])

    def test_uidvalidity_reset_replays_without_duplicates(self):
        m = IMAP(3)
        m.messages = {i: header(i, subject='Questionnaire candidat') for i in range(1, 4)}
        x.scan(self.c, m)
        m.validity = 2
        m.messages = {1: header(3,subject='Questionnaire candidat'),
                      2: header(1,subject='Questionnaire candidat'),
                      3: header(4,subject='Questionnaire candidat')}
        x.scan(self.c, m)
        self.assertEqual(self.c.execute('SELECT count(*) FROM work').fetchone()[0], 4)
        self.assertEqual(self.c.execute('SELECT validity FROM cursors').fetchone()[0], '2')

    def test_fetch_failure_preserves_page_cursor(self):
        m = IMAP(4)
        m.messages = {i:header(i,subject='Facture prestation') for i in range(1,5)}
        x.scan(self.c, m, chunk=2)
        m.fail = 4
        with self.assertRaises(OSError):
            x.scan(self.c, m, chunk=2)
        self.assertEqual(self.c.execute('SELECT fresh_uid FROM cursors').fetchone()[0], 2)
        self.assertEqual(self.c.execute('SELECT count(*) FROM work').fetchone()[0], 2)
        m.fail = None
        self.assertEqual(x.scan(self.c, m, chunk=2), 2)

    def test_search_error_preserves_cursor(self):
        m = IMAP(3)
        x.scan(self.c, m, chunk=1)
        before = tuple(self.c.execute('SELECT * FROM cursors').fetchone())
        m.fail = 'search'
        with self.assertRaises(RuntimeError):
            x.scan(self.c, m)
        self.assertEqual(tuple(self.c.execute('SELECT * FROM cursors').fetchone()), before)

    def test_unknown_header_parsing_is_review(self):
        m = IMAP(1)
        m.messages[1] = b'bad header\xff\n\n'
        x.scan(self.c, m)
        self.assertEqual(self.c.execute('SELECT kind,state FROM work').fetchone()[:], ('mail_review', 'NEEDS_HUMAN'))

    def test_no_trust_in_spoofed_headers(self):
        self.assertIsNone(x.classify(header(extra='Authentication-Results: mx; dkim=pass\r\nX-Verified: true')))

    def test_negative_never_authorizes(self):
        self.assertIsNone(x.classify(header(subject='Not interested, stop contacting us')))

    def test_quoted_positive_never_authorizes(self):
        self.assertIsNone(x.classify(header(subject='Re: interested', extra='\r\nNo thanks\r\n> Can you quote?')))

    def test_mail_cannot_send(self):
        m = IMAP(3)
        for i, subject in enumerate(('interested', 'not interested', '> interested'), 1):
            m.messages[i] = header(i, subject=subject)
        with mock.patch('smtplib.SMTP', side_effect=AssertionError('SMTP forbidden')), \
             mock.patch('smtplib.SMTP_SSL', side_effect=AssertionError('SMTP forbidden')), \
             mock.patch.object(x, 'existing_credentials', side_effect=AssertionError('credentials forbidden')):
            result = x.cycle(self.c, connection_factory=lambda: m, heartbeat=self.path.parent / 'heartbeat.json', now=100)
        self.assertEqual(result['external_actions'], 0)
        self.assertEqual(result['missions']['MONEY']['tasks'], {})
        self.assertTrue(m.closed)

    def test_stale_scanner_and_stalled_progression(self):
        self.task(now=1)
        x.scan(self.c, IMAP(), now=100000)
        self.assertEqual(x.summary(self.c, 100001)['status'], 'STALLED')
        self.assertEqual(x.summary(self.c, 101000)['status'], 'SCANNER_STALE')

    def test_sanitized_error_output_private_files(self):
        m = IMAP(1)
        m.fail = 1
        path = self.path.parent / 'heartbeat.json'
        result = x.cycle(self.c, connection_factory=lambda: m, heartbeat=path, now=100)
        self.assertEqual(result['status'], 'ERROR')
        output = path.read_text()
        self.assertNotIn('secret address', output)
        self.assertNotIn('@', output)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(json.loads(output), result)

    def test_no_content_or_addresses_persisted(self):
        m = IMAP(1)
        m.messages[1] = header(extra='X-Private: bank-account-secret')
        x.scan(self.c, m)
        dump = '\n'.join(self.c.iterdump())
        for secret in ('untrusted@', 'bank-account-secret', 'Message-ID', 'Hello'):
            self.assertNotIn(secret, dump)

    def test_all_mail_missing_fails_closed(self):
        m = IMAP()
        m.list = lambda: ('OK', [b'(\\Inbox) "/" "INBOX"'])
        with self.assertRaises(RuntimeError):
            x.scan(self.c, m)
        self.assertIsNone(m.selected)

    def test_all_mail_literal_and_escaped_names(self):
        m = IMAP()
        m.list = lambda: ('OK', [(b'(\\All) "/" {3}', b'a"b')])
        self.assertEqual(x.all_mail(m), b'"a\\"b"')

    def test_scanner_lock_excludes_second_process(self):
        fd = os.open(str(self.path) + '.scan.lock', os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):
                x.scan(self.c, IMAP(1))
            self.assertEqual(self.c.execute('SELECT count(*) FROM cursors').fetchone()[0], 0)
        finally:
            os.close(fd)

    def test_invalid_staging_is_atomic(self):
        with self.assertRaises(ValueError):
            self.task(independent_verification='not a hash')
        self.assertEqual(self.c.execute('SELECT count(*) FROM events').fetchone()[0], 0)
        self.assertEqual(self.c.execute('SELECT count(*) FROM evidence').fetchone()[0], 0)
        with self.assertRaises(ValueError):
            self.task(deadline='private raw data')

    def test_reset_fetch_error_does_not_skip_reset_history(self):
        m = IMAP(2)
        m.messages = {i:header(i,subject='Questionnaire candidat') for i in range(1,3)}
        x.scan(self.c, m)
        m.validity = 2
        m.messages[1] = header(100,subject='Questionnaire candidat')
        m.fail = 1
        with self.assertRaises(OSError):
            x.scan(self.c, m)
        row = self.c.execute('SELECT * FROM cursors').fetchone()
        self.assertEqual((row['validity'], row['historical_uid']), ('2', 0))
        m.fail = None
        x.scan(self.c, m)
        self.assertEqual(self.c.execute('SELECT count(*) FROM work').fetchone()[0], 3)

    def test_fetch_uid_mismatch_preserves_cursor(self):
        m = IMAP(1)
        original = m.uid
        def mismatched(command, *args):
            if command == 'fetch':
                return 'OK', [(b'1 (UID 99 BODY[HEADER]', header())]
            return original(command, *args)
        m.uid = mismatched
        with self.assertRaises(RuntimeError):
            x.scan(self.c, m)
        self.assertEqual(self.c.execute('SELECT historical_uid FROM cursors').fetchone()[0], 0)

    def test_sparse_deleted_uids(self):
        m = IMAP(10)
        m.messages = {10: header(10)}
        for _ in range(5):
            x.scan(self.c, m, chunk=2)
        self.assertEqual(m.fetches, [10])


if __name__ == '__main__':
    unittest.main()
