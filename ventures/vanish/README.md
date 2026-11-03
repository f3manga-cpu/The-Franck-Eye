# VANISH — publishable build

VANISH is a full-screen cinematic entry followed by a claimable shared wall. It sells one $9,999 one-time, 12-second digital moment and one optional handwritten/textual inscription. This is **not** an investment or a token.

## Modes

- **Local demo:** `npm start`, open `http://localhost:3000/?preview=1`. No payments can occur without explicitly configured secrets and flags.
- **Public exhibition (safe):** deploy on Render using `NODE_ENV=production`, `ACCEPT_REAL_PAYMENTS=false`, `LEGAL_APPROVED=false`. The public will see the door and wall; purchase is disabled.
- **Live sales (not approved here):** requires durable storage, reviewed merchant/consumer terms and tax handling, test-mode Stripe end-to-end, live server Stripe secrets, signed webhook URL, verified fulfillment and real iPhone/Android testing. Enable only after all prerequisites, then set `ACCEPT_REAL_PAYMENTS=true`.

Existing Stripe live catalog: `prod_VYTYlWYcQ8YMSS`, USD one-time `price_1UXMbHJglFhP7gGVTdQ9mD67` ($9,999). These are catalog identifiers, not credentials.

## API

`/healthz`, `/api/config`, `/api/wall`, `/api/checkout`, `/api/payment`, `/api/experience/start`, `/api/experience/inscribe`, `/api/receipt/{id}`, `/api/admin/pending`, `/api/admin/moderate`, `/api/stripe-webhook`. Moderation requires an admin token of at least 24 characters. Script hashes are included in CSP.

## Run

Node 22.13+ with built-in SQLite. `npm test` runs backend tests; `npm start` runs the app. The single HTML file embeds all imagery and front-end code so Render does not depend on third-party CDNs or runtime image services.

### Hosting

A free Render web service has ephemeral storage: **never enable paid transactions with default SQLite on free Render**. Use a persistent disk or external durable database for production. The machine can restart at any time.

`PUBLIC_ORIGIN` must be set to the exact public https origin. `DATA_DIR` is the persistent database folder. Serve a health check at `/healthz`. The sitemap is generated at `/sitemap.xml`; robots.txt advertises it. The homepage is indexable but there is no guarantee of inclusion in Google Search without a live crawl, and submitting Search Console requires site verification.

### Stripe

To enable in an approved durable production environment, add server-side `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID`, `ADMIN_TOKEN`, `PUBLIC_ORIGIN`, `LEGAL_APPROVED=true`, `ACCEPT_REAL_PAYMENTS=true`. Never put these in source, browser, logs or .env committed to Git. Webhook event subscriptions: `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `charge.refunded`. The app verifies signed webhook payloads and paid session status, and enforces one finite moment per paid session and one submitted inscription.

## Visual QA

Chromium in-memory desktop/mobile tests were run because this execution environment blocks localhost navigation in browser sandboxes. Actual Safari device performance, full film-grade mastering and live payment acceptance are NOT verified. Browser-safe preview requires a server because production CSP is applied only there; open stand-alone HTML directly from a file to try a demo without a server.
