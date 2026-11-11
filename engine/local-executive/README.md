# Unattended Outcome Executive (local Linux)

**Deployed:** systemd user service `outcome-executive.service` on an authorized PC.
This is a working persistent execution kernel, not a proven customer-acquisition or funds-settlement system.

## Operating services
- `outcome-operator.service`: existing six-source public lead scanner (research only, six-hour source cooldown).
- `outcome-executive.service`: persistent event loop, Gmail IMAP watcher, private SQLite side-effect ledger, guarded response executor and bounded ChatGPT-login Codex strategy worker.
- Separate ChatGPT money/job automations have additional connected tools; those connections do NOT transfer to the Linux worker.

## What the executive actually does
- Every 300 seconds, checks the existing personal Gmail inbox using an **already available private Gmail credential**. Fetches message headers first and full bodies only for prior, explicitly trusted commercial correspondents.
- POTENTIALLY supports a scoped reply, but automatic sending is DISABLED in the deployed unit after adversarial testing showed false-positive intent classification. Keep disabled until sender authentication, quote-stripping, stronger negative-intent tests and end-to-end acceptance are verified. Does not request advances, enter a contract, offer guaranteed results, or follow up after a rejection.
- Before any SMTP side effect, reserves an idempotency key in owner-private SQLite. Uncertain sends are never automatically retried.
- Runs a bounded noninteractive Codex reasoning cycle at most every eight hours, only when `codex login status` proves **ChatGPT authentication**, never on an API key. Public listing text is treated as untrusted. Suggestions remain private and unverified until separately acted upon.
- Creates owner-private `executive_private/health.json` and SQLite records. NO private correspondence, recipient addresses, credentials, payment account IDs, or bank details are pushed to the public repository.
- The existing job SMTP delivery bridge is deliberately DISABLED in this service: its expected immutable publication ledger is missing from the configured remote repository; attempting live sends would be untracked.
- No money movement, fundraising publication, speculative tokens, sales without deliverability, new paid APIs or mass outreach.

## Commands
```bash
systemctl --user status outcome-executive.service
systemctl --user status outcome-operator.service
python3 -m unittest -v test_executive_runtime  # scanner tests are in the separate local watcher
python3 executive_runtime.py status
journalctl --user -u outcome-executive.service -n 30 --no-pager
systemctl --user restart outcome-executive.service
systemctl --user stop outcome-executive.service
```

## Failure recovery
The user service has `Restart=always`, persisted SQLite WAL, per-message and per-side-effect idempotency keys, and a durable Codex cooldown even if the Codex command times out. The service checks existing Gmail credentials on each cycle. Failure to read Gmail is recorded as an error; it must never be interpreted as "no buyer replied".

## Success criteria and limitations
A running process, a successful Codex plan, an SMTP acceptance and an actual paid sale are DISTINCT stages. Current acceptance: live inbox polling, a bounded model invocation, 11 tests, systemd startup, and persistence are tested. Future full commercial completion still requires a qualified payer, accepted scope, delivered service, verified payment, net fees and bank settlement.

**Source/engineering note:** local systemd configuration and owner-private correspondent allowlist are machine-specific. Never commit the private directory.

## 2026-11-11 adversarial finding
The Gmail reply classifier treated some explicit rejections as positive interest and did not check SPF/DKIM/DMARC. The earlier live --send-replies flag was removed from deployed service and source unit. No auto-replies are enabled. Moreover, 879 inbox messages in 30 days exceed the 450-message scan cap, so historical completeness is NOT established. Standalone PR tests are ten executive tests; combined watcher tests require the other repository.
