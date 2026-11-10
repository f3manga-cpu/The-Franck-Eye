# Autonomous operator: actual boundary

- Cloud: GitHub Actions executes public opportunity checks every five minutes on a best-effort schedule. Persistent state survives runner termination through GitHub commits. Uses no API key or paid model calls.
- On a trusted Linux PC: run python3 -m engine.runtime.operator forever --interval 300 --codex to keep a process alive; use the supplied systemd user service. A separate existing ChatGPT-authenticated Codex CLI session can provide one read-only, evidence-seeking agent investigation per day. CLI refuses API-key auth.
- Local installation is NOT complete until the connected computer is reachable, the repository is checked out at ~/The-Franck-Eye, Codex login is verified, and systemctl --user enable --now franck-eye-operator.service has succeeded. This unit file alone does not install the service.
- This version has no access to ChatGPT Gmail, Stripe, Apollo or user bank credentials. It cannot claim verified payments, send sales messages, post product listings or deliver paid work.
- Do not import credentials into this public repo. No additional spending or payments authorized.
- Validate with python3 -m unittest discover -s engine/runtime/tests -v.
- Cloud status: see the autonomous-operator GitHub Actions workflow. This is a bounded recurring execution system, not continuous every-second LLM reasoning.
