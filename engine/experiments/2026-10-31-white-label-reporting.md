# Experiment 2026-10-31 — white-label reporting for creative and acquisition agencies

**Objective:** confirm the first new, attributable live Stripe payment, not merely produce collateral. **Cost:** €0 cash, excluding working time. **Status:** active, no payment confirmed.

## Market/channel alternatives researched on 2026-10-31

| Model | Verified commercial mechanism | Cost/fees | Demand/access limitation | Decision |
| --- | --- | --- | --- | --- |
| Ko-fi digital shop or commissions | Seller lists downloadable assets or accepts service commissions; buyer pays through connected Stripe/PayPal directly | No listing/monthly fee; 5% on shop/commissions + processor fees; free sellers can list up to 600 items | No evidence of meaningful built-in buyer discovery; depends on own audience and would require account setup | Hold; viable later with distribution |
| Gumroad digital downloads | Direct checkout or Discover marketplace | 10% + $0.50 direct (processing additional); 30% through Discover | Discover has potentially higher discovery but expensive margin, no evidence of demand for our specific product | Hold; evaluate when differentiated digital product validated |
| itch.io indie game audio assets | Direct-to-Stripe sales and pay-what-you-want; seller chooses platform revenue share | 10% default share, adjustable 0–100%; card processor fees separate (docs example 2.9% + $0.30) | FeelGoodBangers Stripe connection exists; audio product prepared, but public product page/upload not verified | Hold until listing exists; no fabricated marketplace revenue |
| B2B agency reporting microservice | Sell a real service using already-live €59 Stripe checkout, without platform intermediary | €0 new cash cost; standard Stripe processing applies | Requires reaching a suitable agency and getting a reply/brief | **Run a 2-contact test now** |

**Sources (official):**
- Ko-fi Shop https://help.ko-fi.com/hc/en-us/articles/360009712917-Ko-fi-Shop-Sell-digital-physical-products and https://ko-fi.com/pricing
- Gumroad https://gumroad.com/pricing and https://gumroad.com/help/article/66-gumroads-fees
- itch.io https://itch.io/docs/creators/payments and https://itch.io/docs/general/about

These are platform terms, not sales-volume evidence. None of these sources demonstrates that our offer will sell.

## Test chosen: agency subcontracting, not a generic blast

A €59 small-scope report (one channel, five KPIs, 3–4-page PDF, three working days after complete anonymized inputs) is already purchasable at https://buy.stripe.com/4gM9AUe0O9nE8YE2FM43S00. Example deliverable is explicitly synthetic. The pitch addresses agencies that may need analytical reporting capacity to complement campaign/content execution.

**2026-10-31 verified actions:** two individually tailored business emails sent using connected Gmail, to Lyon Marketing Co (creative/social media) and Net Strategy (SEO/acquisition). Recipients' public business contact addresses were verified on their official websites before sending. Prior-sent searches found no previous message to either address. Gmail returned a sent-message ID for each. The IDs and recipients are retained in private Gmail, not this public repository. No replies or paid orders confirmed at the time of sending.

- Lyon Marketing Co site: https://www.lyonmarketingco.com/ (public contact listed)
- Net Strategy contact: https://net-strategy.fr/contact/

**Published supporting offer:** [white-label reporting](../../offers/renfort-reporting-marque-blanche.md), using an already-live checkout. No new payment product or price invented.

## Measurement and stop rule

- Primary: number and amount of new **verified** live Stripe payments attributable to this offer, net of fees/refunds (not historical physical-product transactions).
- Secondary: genuine human replies, qualified briefs, paid conversions. Messages sent are only input metrics.
- Review after **five business days** from 2026-10-31 (around 2026-11-06). If no qualified interest, **stop this pitch** rather than send repeated messages to the same contacts; switch buyer segment or offer. Do not claim marketplace traction from price listings alone.
- No ad spend, paid subscriptions, unsolicited mass mailing, or speculative token launches.
- **At review:** compare with the itch.io product listing status and other new channels; favor the channel showing real buyer intent.

## Stripe reconciliation

Connected live account Ømint was queried via the Stripe API on 2026-10-31. It returned **five** succeeded PaymentIntents, all pre-existing physical-product transactions; **zero new confirmed payments** attributable to this experiment. Do not write those old payments into this experiment's revenue ledger. Customer names, addresses, transaction IDs and payment secrets were intentionally excluded from public files.

## Research engine health

The scheduled GitHub workflow `.github/workflows/opportunity-research.yml` is present with a 06:19 UTC cron and a manual dispatch. At this run, neither `engine/data/opportunities.json` nor `engine/data/RESEARCH.md` existed on the default branch, and no 'Update opportunity research queue' commit was found. Therefore **successful scheduled execution is not confirmed**; this is not evidence that it definitely failed (the schedule may have been delayed/disabled). Verify the Actions run log and whether scheduled workflows are enabled before modifying the code. This experiment does not invent a research output.
