# Revenue harness — independent validation report

Audit run (UTC): 2026-11-06T08:04:58+00:00

> This is a **public, manually updated operations state**. It has no direct
> access to Stripe, Gmail, bank balances or delivery confirmations.
> The live Stripe connector is the source of truth for payment claims.

Active experiment: \`prevol_facture_20261103\`

| Experiment | Stage | Purchases recorded | Gross recorded (€) | Net recorded (€) |
|---|---|---:|---:|---:|
| prevol_facture_20261103 | distributed | 0 | 0.00 | unknown |
| comeup_buyer_intent_20261102 | prepared | 0 | 0.00 | unknown |

## Invariants and warnings

- State invariants pass; **no independent payment verification performed**.
- prevol_facture_20261103: NET_UNKNOWN_NEVER_EQUATE_GROSS_TO_NET
- prevol_facture_20261103: ZERO_CONFIRMED_PURCHASES_IN_RECORDED_STATE
- comeup_buyer_intent_20261102: NET_UNKNOWN_NEVER_EQUATE_GROSS_TO_NET
- comeup_buyer_intent_20261102: ZERO_CONFIRMED_PURCHASES_IN_RECORDED_STATE
- comeup_buyer_intent_20261102: NOT_LIVE_IN_BUYER_CHANNEL

## Ledger notes

- Existing ledger events: 5
- Manually recorded gross: €0.00; not independently verified from Stripe.
- Model-agent/API costs: no API inference performed by this auditor.
- Next decision must be supported by buyer exposure, response or payment, not file counts.
