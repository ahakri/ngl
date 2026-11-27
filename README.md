# Siteline

**Data-centre siting records.** Siteline reads the public legislative record of US city and county governments every day and turns it into structured data on where data centres are being approved, stalled or blocked: project entitlements, moratoria and code changes, incentives, and power and water deals.

Why this business, and what else was considered: [reports/Highest EV niche data business.md](reports/Highest%20EV%20niche%20data%20business.md).

## What it does

- **Collects** matching agenda items and legislation from 49 jurisdictions in 20 states through the official Legistar Web API, with the full action history (each hearing, vote and tally) for every siting record.
- **Classifies** each item by rule into project entitlement, policy, incentive, or power and water; flags restrictive actions (moratoria, bans, formal opposition); and filters out a government's own IT contracts, which share the words "data center".
- **Extracts** acreage, square footage, megawatts, project name, case number and staff recommendation from the official text, and normalises local status labels into approved / denied / continued / withdrawn / pending.
- **Sells access:** a free tier that runs 30 days behind, and paid plans (Pro $399/month, Team $750/month — edit in `server/plans.js`) with live records, an upcoming-hearings calendar, saved watches with private Atom feeds, CSV export and an API. Stripe Checkout is built in.

On the first full run it collected 546 items, of which 312 are siting records. Restrictive actions in the covered jurisdictions went from 3 in 2025 to 35 in 2026.

## Run it

Requires Node 22.13+. No database server, no native modules.

```bash
npm install
npm run build        # builds the web app into web/dist
npm start            # http://localhost:8080
```

With an empty database the server runs a full collection on start (about four minutes) and then daily at 09:00 UTC. To collect by hand:

```bash
npm run collect                       # everything
npm run collect -- --only=mesa,phoenix
npm run collect -- --reclassify       # re-derive fields after changing the rules
```

Other commands: `npm test`, `npm run dev`, `npm run web:dev`. Configuration is by environment variable — see [.env.example](.env.example).

## Taking payments

1. In Stripe, create two recurring monthly prices (Pro, Team).
2. Set `STRIPE_SECRET_KEY`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_TEAM` and `PUBLIC_URL`.
3. Add a webhook at `<PUBLIC_URL>/api/billing/webhook` for `checkout.session.completed`, `customer.subscription.updated` and `customer.subscription.deleted`; set its signing secret as `STRIPE_WEBHOOK_SECRET`.

Without these the pricing page shows a contact link (`SALES_EMAIL`). To set a plan by hand: `UPDATE users SET plan = 'pro' WHERE email = '…'`.

## Layout

```
server/
  jurisdictions.js        coverage list — add a row to add a government
  collectors/legistar.js  the source adapter
  classify.js             categories, size extraction, outcomes (pure, tested)
  store.js collect.js     persistence and the collection run
  queries.js plans.js     API payloads, filters, feeds, tiers
  auth.js billing.js app.js index.js
web/                      React + Vite front end
test/                     node:test suites (classifier cases are real agenda items)
reports/, research_notes/ the research behind the choice
```

The API is documented in the app at `/docs`.

## Known limits

- **Coverage is partial.** Only governments on Legistar are read. Northern Virginia, the largest US data-centre market, mostly publishes through other systems and is not covered yet. Next sources, in order of value: other agenda platforms (Granicus, CivicClerk, BoardDocs), state air permits for on-site generation, and utility-commission large-load dockets.
- **Title-only matching.** Items that mention data centres only in an attachment are missed.
- **Classification is rule-based and unmeasured.** It was tuned by reading samples, not scored against a labelled set. Build that set before quoting an accuracy figure to customers.
- **Demand is unvalidated.** Prices are anchored on a neighbouring product's public list price; no buyer has been asked. Talk to five prospective customers before investing further.

## Before launch

- Read the Legistar API terms and each covered government's reuse terms for commercial redistribution.
- Have the Terms and Privacy drafts in `web/src/pages/Legal.jsx` reviewed.
- Add email verification and a forgotten-password flow (needs an email provider).
- SQLite on one node is fine to launch; move to Postgres for more than one instance.
