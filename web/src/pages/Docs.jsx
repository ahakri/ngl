import { Link } from 'react-router-dom';

const origin = typeof window === 'undefined' ? '' : window.location.origin;

const ENDPOINTS = [
  ['GET /v1/meta', 'Your plan and its limits, plus the allowed values for category, outcome and state.'],
  ['GET /v1/summary', 'Public. Headline counts, activity per quarter by type, activity by state, and project outcomes.'],
  ['GET /v1/jurisdictions', 'Public. Every covered government with its record count, latest activity and last successful check.'],
  ['GET /v1/records?state=AZ&category=project&limit=50', 'Siting records, newest first. Filters: state, jurisdiction, category, outcome, restrictive=1, since, until (YYYY-MM-DD), q (text search). Page with limit and offset.'],
  ['GET /v1/records/{id}', 'One record with its full official text and action history (each hearing, action, result and vote tally).'],
  ['GET /v1/upcoming', 'Records on a published future agenda, soonest first. Pro and Team.'],
  ['GET /v1/export/records.csv', 'All records matching the same filters, as CSV. Pro and Team.'],
  ['GET /feeds/{token}', 'Atom feed for a saved watch. Create watches from the Records page; the link is private to you.'],
];

const FIELDS = [
  ['category', 'project (rezoning, use permit, site plan, plat and similar entitlements), policy (moratoria, code changes, studies, resolutions), incentive (abatements, development agreements) or utility (power, substation and water agreements, large-load rates).'],
  ['restrictive', 'true when a policy item restricts development: a moratorium, ban, cap or formal opposition.'],
  ['outcome', 'approved, denied, continued, withdrawn or pending — normalised from the local status and the most recent action.'],
  ['event_date', 'The latest known activity: the last recorded action, otherwise the agenda date, otherwise the introduction date.'],
  ['acres, square_feet, mw', 'Size figures found in the official text, or null. When several appear, the largest is kept.'],
  ['project_name, case_number, staff_recommendation', 'Extracted from the official text where present.'],
  ['source_url', 'The official record this row was built from.'],
];

export default function Docs() {
  return (
    <div className="docs" style={{ maxWidth: 820 }}>
      <h1>API reference</h1>
      <p style={{ marginTop: 8 }}>A read-only JSON API over the same records as this site. Create a key on your <Link to="/account">account page</Link> and send it as a bearer token.</p>
      <pre>{`curl "${origin}/v1/records?state=TX&restrictive=1" \\
  -H "Authorization: Bearer slk_your_key"`}</pre>

      <h2>Plans and limits</h2>
      <ul>
        <li>Without a paid plan, records from the last 30 days are withheld; list responses report how many in <code>withheld_by_plan</code>.</li>
        <li>Each keyed request counts against a daily quota (Free 100, Pro 5,000, Team 50,000), reset at 00:00 UTC. See <code>x-ratelimit-remaining</code>.</li>
        <li>Errors are <code>{'{ "error": { "code", "message" } }'}</code> with a matching status: 400 invalid filter, 401 invalid key, 402 plan required, 404 not found, 429 quota or rate limit.</li>
      </ul>

      <h2>Endpoints</h2>
      {ENDPOINTS.map(([sig, text]) => (<div key={sig}><h3>{sig}</h3><p>{text}</p></div>))}

      <h2>Record fields</h2>
      {FIELDS.map(([name, text]) => (<div key={name}><h3>{name}</h3><p>{text}</p></div>))}

      <h2>Method and limits</h2>
      <ul>
        <li><b>Source.</b> The public legislative record of each covered government, read through its official API once a day.</li>
        <li><b>Selection.</b> Items whose title mentions data centres, data processing facilities or large loads. A government's own server rooms and IT contracts are detected and excluded.</li>
        <li><b>Classification.</b> Rule-based and deterministic. It can misfile an item; the official text is always returned so you can check.</li>
        <li><b>Gaps.</b> Coverage is the jurisdictions listed on the <Link to="/coverage">coverage page</Link>, not the whole country. Items discussed only in attachments, not in the agenda title, are missed.</li>
      </ul>
    </div>
  );
}
