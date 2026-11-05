# The Franck Eye — instructions for coding agents

## Mission and evidence standard
Turn a clearly stated objective into a **tested change and reviewable pull request**. Optimize for user value and independent discovery, not file count, prose, or repeated plans. A successful CI run proves only those checks passed; it does not prove product quality, deployment, customer reach, or revenue.

## Start every engineering task
1. Inspect the actual repository, Git status, existing tests, and the intended user-facing outcome. Don't overwrite uncommitted work.
2. Locate existing approaches in this repo before adding a framework. When architecture materially matters, compare at least two established alternatives using primary documentation, state the choice and tradeoff briefly, then implement the smallest sound approach.
3. Write concrete acceptance criteria that can be verified independently: tests, a user journey, a functioning URL, or authoritative external data as appropriate.
4. Work on a dedicated task branch. Prefer one coherent, small change over an unbounded rewrite.
5. Implement the change, including deterministic regression tests where feasible. Run `python3 tools/verify_agent_work.py`; if the change involves a UI, also run a real browser test or explicitly report why no browser was available.
6. Review your own diff and request an independent coding-agent review when available. Correct defects, rerun checks, and produce a PR with evidence, limitations, and remaining blockers.

## Mandatory local verification
`python3 tools/verify_agent_work.py` runs the existing standard-library Python test suites, the harness's own tests, and Git whitespace checks. The command exits nonzero on failure. Never claim tests ran if they didn't; never mark a simulated or unit-tested external service as live.

## Commercial and production boundaries
Read `engine/harness/OPERATING_CONTRACT.md` before changing revenue or outreach logic. Do not confuse a documented offer, a checkout link, a successful HTTP response, or an outreach draft with a verified sale. Keep customer and payment information out of this public repository. Do not send emails, incur API costs, purchase anything, alter production services, trigger real trades, or merge/deploy without explicit authorization for the specific action. Use test fixtures and mocks by default.

## Minimum PR report
- Objective and acceptance criteria
- Evidence of implementation (changed files and what works)
- Exact verification commands and their results
- Independent review and any unresolved findings
- Real-world status: prepared / tested / deployed / verified in use / revenue verified, as applicable
- Blockers and next action (without asserting future success)

## Escalation rule
If execution is blocked, identify the **specific missing permission, credential, environment, or external dependency** and show the shortest safe unblock. Do not replace an executable task with extensive ideation.
