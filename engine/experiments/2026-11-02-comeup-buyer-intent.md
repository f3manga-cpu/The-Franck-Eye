# 2026-11-02 — Buyer-intent distribution test: ComeUp service (not yet live)

## Evidence / infrastructure checks

- GitHub Actions workflow file confirmed on default branch: `.github/workflows/opportunity-research.yml`, daily schedule `19 6 * * *`, `workflow_dispatch`, Python tests and `discover`, then commits `engine/data/opportunities.json` and `engine/data/RESEARCH.md`.
- Latest research output read: `engine/data/RESEARCH.md` and `opportunities.json`, **updated 2026-11-01 13:27:02 UTC** via commit `d31967947316b830af360ee8a28a13f37af60884`. `errors: []`. This proves a recent output update but **does not prove the 2026-11-02 scheduled run completed**; run-list access is not exposed by the connected GitHub tools, and no new output commit is visible. Do not report today's scheduled run as succeeded.
- Queue remains noisy and non-commercially validated (IKEA UK resale, unrelated billing incident, generic creator site). **Do not promote keyword scores to demand evidence.**
- Stripe Ømint connected **livemode**: `GetPaymentIntents` list read on 2026-11-02; exactly **five** total succeeded intents, all created before 2026-10-30, and **zero** PaymentIntents created since 2026-10-30 UTC. None attributed to AUDIT-MKT-01, INSIGHTS-01, KPI-DASH-01 or experiments. **New verified Stripe gross revenue 0 €; net revenue 0 €**. Historic physical transactions excluded. No customer IDs, payment IDs or banking information written here.
- `engine/data/events.jsonl` previously contains only experiment and publication events; no `payment_confirmed` events. No new payment event added.

## 3 distinct routes checked (official sources, 2026-11-02)

| Route | Mechanism and official evidence | Eligibility, fees and actual demand signal | Decision |
|---|---|---|---|
| **ComeUp** — French-language fixed-scope analytics services | Buyers order a digital service and pay inside ComeUp; seller delivers through platform; money is released on acceptance / platform rules. Official seller terms: https://support-fr.comeup.com/article/1609-comment-devenir-vendeur and https://support-fr.comeup.com/article/1633-pourquoi-comeup-est-une-plateforme-sure-pour-mes-ventes | Free seller plan, 20% commission on pre-tax order amount; max 6 services; no promotion boost: https://support-fr.comeup.com/article/1610-quelle-est-la-commission-prise-sur-le-montant-de-la-commande and https://support-fr.comeup.com/article/1613-quels-sont-les-avantages-dune-offre-comeup-plus-et-comment-souscrire . Official pricing allows €15+ in €5 increments: https://support-fr.comeup.com/article/1628-comment-fonctionne-la-tarification-et-comment-bien-la-choisir . Public category shows **353 competing services** (not buyers) and reviews for established sellers: https://comeup.com/fr/category/analyse-de-donnees/services . These are demand proxies, not expected conversion rates. | **SELECT**. New channel with native buyer intent and no upfront fee. A focused listing can be drafted now; seller registration/validation and final listing require authorized user access. |
| **User Sense** — paid UX research participation | Participant tests / interviews pay by bank transfer, usually within **two business days** of a completed session: https://www.usersense.fr/user-tester | No registration fee; Europe residents accepted; screeners, own webcam/mic/internet required; 20-min unmoderated test **€15**, moderated **€22.50–€100**, questionnaires **€5–€50** (ranges are offered rewards, not earnings). No guarantee of invitations; cannot automate personal test participation. | **WATCH** as potential personal cash supplement, not a scalable business. |
| **UserTesting** — paid usability tests | Approved participants perform genuine user tests; rewards shown per test; USD via PayPal, paid ~**14 days** after test: https://www.usertesting.com/fr/etre-payer-pour-tester/gagner-de-l-argent-en-ligne and https://participant-support.usertesting.com/hc/fr/articles/38814220821523-FAQ-Paiements | Supports French or English, applicants outside US allowed subject to acceptance; practice test unpaid: https://www.usertesting.com/fr/etre-payer-pour-tester/commencer-maintenant . Requires applicant's own effort and verified PayPal; longer settlement. | **HOLD** relative to faster User Sense / higher-value services. |

## Execution on 2026-11-02

- Created [complete ready-to-list ComeUp seller copy](../../offers/comeup-audit-campagne-ready-to-list.md), with 55 € base service, 3-day deadline, one anonymized export (≤2,000 rows / 20 columns), up to 3 KPI, 2-page PDF, 3 insights and up to 3 recommendations, bounded revision, FAQ, profile, intake questions and delivery constraints.
- Verified ComeUp prohibits external contact details and off-platform payment in service copy: https://support-fr.comeup.com/article/1608-quels-sont-les-elements-non-autorises-dans-les-textes-les-images-des-services-et-votre-profil . **No Stripe links or contact addresses appear in listing copy**. Never steer ComeUp buyers to external checkout.
- Public GitHub file is a **draft**, **not a live ComeUp listing**. No account registration, identity submission, marketplace publication, cold outreach or expense made.
- The first marketplace service would be a differentiated decision-oriented marketing audit, not another generic dashboard. Existing public synthetic audit example may be adapted to a marketplace-compliant portfolio visual with explicit synthetic label.
- Economics: at €55 and 20% ComeUp commission, **€44 pre-tax, pre-other-fees** if a legitimate paid order completes; zero until confirmed. ComeUp money must be reconciled separately from Ømint Stripe.

## Single blocker and smallest action

No confirmed ComeUp seller account / authenticated publishing capability. Gmail search for ComeUp-related emails found none (not proof that no account exists). **One-time user action:** sign in or create the free ComeUp seller account and complete its required identity validation; then supply the public seller profile URL. The listing copy is already prepared, but final submission requires authorized dashboard access. Do not ask for passwords or identity documents in chat.

## Go / no-go

- State: **DRAFT_READY**, not `listing_live`; zero impressions, conversations, orders and receipts claimed.
- On live publication: measure **10 business days** of actual listing exposure; primary KPI completed paid orders and verified seller balance/payout, secondary qualified conversations. No bought traffic, no spam.
- If zero buyer signals after first cycle, revise positioning once; after another cycle without signal, pivot. Do not spend on ComeUp Plus until commission savings are justified by completed sales.
- Stop repeating generic B2B email templates as a default; marketplace-native buyer intent is the new acquisition hypothesis.
