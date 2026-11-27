# Uptake

**AI ecosystem adoption data.** Uptake tracks what AI developers actually adopt — model SDKs, agent frameworks, vector databases, inference runtimes and open models — and sells the result as market share, momentum and breakout signals through a web app and an API.

Why this niche, and what was considered instead: [docs/RESEARCH.md](docs/RESEARCH.md).

## What it does

- **Collects daily** from public sources: PyPI download logs (via pypistats), the npm downloads API, the Hugging Face Hub and Hacker News.
- **Cleans** the data: detects registry-wide counting changes ("structural breaks") and upstream outage days, and never computes growth or share across a break.
- **Derives signals** for 87 projects in 9 competitive categories: 7/28-day and 12-week growth, acceleration, category share and share change, rank, a 0–100 momentum score and a breakout flag.
- **Sells access** in three plans (Free / Pro $199 / Team $999 per month) with API keys, daily quotas, history depth and CSV export gated by plan. Stripe Checkout is built in.

## Run it

Requires Node 22.13+. No database server, no native modules.

```bash
npm install          # server dependencies
npm run build        # installs and builds the web app into web/dist
npm start            # http://localhost:8080
```

On first start with an empty database the server runs a full collection (about four minutes), then repeats daily at 07:00 UTC. To collect on demand:

```bash
npm run collect                  # everything
npm run collect -- --only=npm,hf # some sources: pypi, npm, hn, hf
npm run collect -- --signals-only
```

Other commands: `npm test`, `npm run dev` (server with reload), `npm run web:dev` (Vite dev server proxying to :8080).

Configuration is by environment variable — see [.env.example](.env.example). A `Dockerfile` is included; mount a volume at `/data` to persist the database.

## Taking payments

1. In Stripe, create two recurring monthly prices (Pro, Team).
2. Set `STRIPE_SECRET_KEY`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_TEAM` and `PUBLIC_URL`.
3. Add a webhook endpoint at `<PUBLIC_URL>/api/billing/webhook` for `checkout.session.completed`, `customer.subscription.updated` and `customer.subscription.deleted`; set its signing secret as `STRIPE_WEBHOOK_SECRET`.

Without these the site runs normally and the pricing page shows a contact link (`SALES_EMAIL`) instead of checkout. To set a plan by hand: `UPDATE users SET plan = 'pro' WHERE email = '…'`.

## Layout

```
server/
  catalog.js            tracked projects and categories — edit this to change coverage
  collectors/           one module per source
  pipeline/signals.js   growth, share, momentum, break and gap detection (pure functions)
  store.js queries.js   persistence and API payload assembly
  auth.js billing.js plans.js
  app.js index.js       HTTP API, scheduler
web/                    React + Vite front end
test/                   node:test suites for the pipeline, API, auth and billing
docs/RESEARCH.md        niche research
```

The API is documented in the app at `/docs`.

## Before charging customers

- Have the upstream terms (pypistats/PyPI, npm, Hugging Face, Algolia HN Search) reviewed for commercial redistribution of derived statistics.
- The Terms and Privacy pages (`web/src/pages/Legal.jsx`) are starting drafts: have counsel review them and add your company details.
- Add email verification and a forgotten-password flow (needs an email provider; signed-in users can already change their password).
- SQLite on one node is fine to launch; move to Postgres when you need more than one instance.
