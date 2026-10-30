# Private itch.io performance monitoring

The main bridge can **publish** builds. This second reusable workflow can read **all-time** itch.io project views, downloads, purchase counts, and API-reported earnings. It is intended to run **only in a private GitHub repository**, because Actions logs include commercial performance figures.

For your PRIVATE product repository, set an Actions secret called `ITCH_API_KEY` from your itch.io API keys page (do not share it in chat). Then add the following to `.github/workflows/itch-sales.yml`:

```yaml
name: itch.io business metrics
on:
  workflow_dispatch:
  schedule:
    - cron: '43 7 * * *'
jobs:
  inspect:
    uses: f3manga-cpu/The-Franck-Eye/.github/workflows/itchio-metrics.yml@main
    secrets:
      ITCH_API_KEY: ${{ secrets.ITCH_API_KEY }}
```

This fetches `https://api.itch.io/profile/games` with a bearer token. All-time counters are **not** daily deltas, confirmed live Stripe receipts, or net profit. Sales and payout figures must still be reconciled with Stripe separately. Avoid logging or committing any purchaser identifiers, tokens, or personal data.

GitHub Actions will run the automation without an always-on local PC. To have a ChatGPT automation review these figures, enable its GitHub access to the private repository and instruct it to inspect the latest workflow execution and compare previous snapshots. Do not put private metrics into the public `The-Franck-Eye` repository.

Official documentation: https://itch.io/docs/api/serverside
