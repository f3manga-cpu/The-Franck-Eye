# Durable dual-mission outcome operator v2 — runbook

## Mission contracts

MONEY: maximize legitimately obtained new NET funds verifiably available in the user's BANK. Processor balances, speculative listings and promised payments are not bank cash. Without bank evidence, status is UNKNOWN.

JOB: obtain accepted, paid work. Job discoveries, sent applications, delivery receipts, responses, interviews, offers, accepted work and wages are different stages. Never invent qualifications or personal answers.

## Deployed components on Linux

- outcome-operator.service: lightweight public source scanner, NOT source-confirmed payable work.
- outcome-executive-v2.service: read-only Gmail All Mail ingestion, priority for new mail, bounded historical backfill, two owner-private durable work queues and state-machine transitions.
- outcome-healthguard.timer/service: five-minute watchdog for stuck workers, with max two restarts per hour to prevent crash loops.
- Separate ChatGPT scheduled Money and Job missions, with their own connected apps (not inherited by the Linux worker).

V2 has NO autonomous SMTP, purchases, tokens, funding appeals, job submissions, third-party contracts or bank transfers. A task discovered is not an external action. A bank credit needs independent bank evidence. A job acceptance needs original employer evidence.

## Persistence and security

Owner-private SQLite: ~/outcome-operator/executive_v2_private/state.sqlite3
Owner-private heartbeat: ~/outcome-operator/executive_v2_private/heartbeat.json
Watchdog state: executive_v2_private/watchdog_state.json

The scanner selects Gmail's IMAP folder bearing the All attribute (this French account uses '[Gmail]/Tous les messages') and FETCHes only headers with BODY.PEEK. Separate fresh, recent snapshot and historical UID cursors preserve progress across service restart and handle UIDVALIDITY resets. Cursor advancement is transactional with evidence insertion. New mail is never held behind an old backlog. Unrelated mail never becomes mission work. Neither headers, subjects, body contents, private account IDs, credentials nor recipient addresses may enter the public repository.

Evidence hashes establish deduplication, not payment or sender authenticity. No automatic reply unless security verification and negative-intent safeguards are independently approved and tested.

## Test and operational commands

cd ~/outcome-operator
python3 -m unittest -q test_executive_v2 test_health_guard test_executive_runtime test_mission_watch
python3 executive_v2.py status
python3 health_guard.py status
systemctl --user status outcome-executive-v2.service
systemctl --user status outcome-healthguard.timer
journalctl --user -u outcome-executive-v2.service -n 30 --no-pager
systemctl --user restart outcome-executive-v2.service
systemctl --user stop outcome-executive-v2.service

Owner linger is enabled, so user services continue after logout. Units use Restart=always, memory and CPU quotas, owner-private umask and a failure watchdog. An internet outage, revoked credential, shut-down PC or API change can still stop progress; nobody should promise invulnerable 'forever' reliability.

## Release acceptance gates

1. Feature branch isolates changes and keeps private state local.
2. Unit and integration tests cover 879-message backfill, archived mail, UIDVALIDITY reset, recent-priority, fail-safe pagination, crash leases/retries, spoofing, negative replies and evidence attribution.
3. One real IMAP run must succeed read-only before service activation.
4. At least two service cycles and a controlled restart are verified before claiming persistence.
5. Watchdog timer must run and produce a health record, not simply exist.
6. Public source-only PR should have CI checks before merge; a draft PR is not production main.
7. New external actions require scoped permission, independently verified buyer/employer, dedup key, true deliverability and primary-source receipt.

## Known gates still unmet

- No autonomous buyer acquisition, paid fulfillment or bank connector on Linux. Do not count task processing or Codex advice as revenue.
- Previous job-acquisition SMTP bridge is disabled: its upstream published immutable request ledger is missing. Do not activate or bulk send without repair and verification.
- Two existing Beetween questionnaires require real personal remuneration/severance answers; do not invent or claim submission.
- No production marketplace publication, financial transfer or fundraising campaign is authorized without explicit scoped approval.
- Commercial distribution and employer acceptance must be advanced by the connected agents and authorized existing account workflows. A week of healthy green services but no external actions is an OUTCOME FAILURE, not success.

## Private, traceable queue-to-message bridge

The v2 state contains an owner-private mail_refs table storing a verified Gmail
UID+UIDVALIDITY pointer for each relevant event. It does NOT persist the sender
address, subject, body or private account identifiers in public source files.

    cd ~/outcome-operator
    python3 review_task.py pending --limit 20
    python3 review_task.py inspect --work-id <opaque-64-character-ID> --reveal-private

Inspection fetches the original Gmail message in IMAP read-only mode and must
verify the original stored header hash and UIDVALIDITY before showing an excerpt
to the authorized private operator. Never paste --reveal-private outputs into
public GitHub issues, commits, logs or model prompts beyond the owner's trusted
connected operational context. This is an evidence locator, NOT sender
authentication, customer acceptance or payment proof. The executor must
independently verify trust, lawful authority and every external action.
