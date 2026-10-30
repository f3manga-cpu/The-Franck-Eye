# itch.io publishing bridge (FeelGoodBangers)

## Purpose

ChatGPT can edit the source in GitHub. GitHub Actions can build product files and deliver updates to an already-created itch.io product via itch.io's official `butler` uploader. No Linux PC or paid Desktop Commander subscription is needed.

**Current status: integration code ready, but not connected to an itch.io account and not yet deployed.**

## Non-negotiable setup

1. **Create the first product page** once via https://itch.io/game/new; set its title, price, classification, description, cover image and visibility manually (or with an authorized browser assistant). Butler cannot create pages or set prices. Copy the real project URL: `https://ACTUAL-USERNAME.itch.io/ACTUAL-SLUG`. Account display name may differ from the URL username.
2. For commercial files, use a **PRIVATE GitHub repository**. Never commit the paid ZIP or its full contents to this public repository.
3. Generate an itch.io API credential at https://itch.io/user/settings/api-keys. Make a separate revocable key for CI if possible. **Do not paste it in chat, issues, README files, or source.**
4. In the PRIVATE repository, go to Settings > Secrets and variables > Actions > New repository secret. Name it `BUTLER_API_KEY` and paste the key as its value. GitHub Actions will inject it only at runtime.
5. Put the product archive in `dist/full.zip`, or generate it with an automated build that runs before the publishing job.
6. Create `.github/workflows/itch-release.yml` in the private repository with the example below. Replace the exact URL slug when the page exists.

### Example calling workflow (store this in PRIVATE product repo)

```yaml
name: Release itch.io full version
on:
  workflow_dispatch:
jobs:
  release:
    uses: f3manga-cpu/The-Franck-Eye/.github/workflows/itchio-publish.yml@main
    with:
      target: actual-username/actual-product-slug
      channel: full
      release_path: dist/full.zip
      dry_run: true # preview first; set false to upload for real
    secrets:
      BUTLER_API_KEY: ${{ secrets.BUTLER_API_KEY }}
```

After verifying the first upload, an authorized automation can update the source/build files and change the calling workflow to run on selected pushes. Changes to the same channel are uploaded incrementally.

## What this DOES and DOES NOT automate

- **YES:** packaging if a build step is supplied; uploading and updating binary product files; verifying the command result; later obtaining view/purchase counts from the itch.io API in a private process.
- **NO:** initial project/page creation, product pricing, payout setup, thumbnail and page copy changes via butler. These need itch.io dashboard actions (potentially via a separately authorized browser agent).
- **NO:** creating demand, guaranteeing a sale, or automatically proving that Stripe received net proceeds. That requires reconciled payment evidence.
- **SECURITY:** The shared workflow is public, but the real paid assets, API key and private results must remain in the calling PRIVATE repo. Review workflow changes before allowing secrets to be used.
- **SAFETY:** Default is `dry_run: true`. A real upload only happens after changing it to `false`. Do not trigger with a guessed username or project slug.

Useful official docs: https://itch.io/docs/butler/pushing.html and https://itch.io/docs/butler/login.html

## Next user action

Supply only the **public URL of the first product page** and put the API key in the GitHub Actions secret as described. Never send the key to ChatGPT.
