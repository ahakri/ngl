import { Link } from 'react-router-dom';

const origin = typeof window === 'undefined' ? '' : window.location.origin;

const ENDPOINTS = [
  ['GET /v1/meta', 'Your access tier, the minimum cohort size, and every dimension with its allowed values and labels.'],
  ['GET /v1/summary', 'Public. Dataset size and median deal value by sport and by deal type.'],
  ['GET /v1/benchmarks?group_by=sport&level=power4', 'Percentile bands for a filtered cohort, broken down by one dimension. Filters: sport, level, deal_type, payer_type, followers, industry, class_year, region, clearance. group_by also accepts quarter.'],
  ['GET /v1/comps?sport=football&limit=50', 'Anonymised individual deals in a cohort, newest first. Empty when the cohort is below the minimum size.'],
  ['POST /v1/rangefinder', 'Body: sport, level, deal_type, payer_type, followers, and optionally amount. Returns the comparable cohort, its range, where the amount sits, and the closest deals.'],
  ['GET /v1/export/benchmarks.csv?group_by=sport', 'The benchmarks breakdown as CSV. Pro and Team.'],
];

export default function Docs() {
  return (
    <div className="docs" style={{ maxWidth: 820 }}>
      <h1>API reference</h1>
      <p style={{ marginTop: 8 }}>A JSON API over the same benchmarks as this site. Create a key on your <Link to="/account">account page</Link> and send it as a bearer token.</p>
      <pre>{`curl -X POST ${origin}/v1/rangefinder \\
  -H "Authorization: Bearer rfk_your_key" \\
  -H "Content-Type: application/json" \\
  -d '{"sport":"womens_basketball","level":"power4","deal_type":"social_post",
       "payer_type":"national_brand","followers":42000,"amount":2500}'`}</pre>

      <h2>Access and limits</h2>
      <ul>
        <li>Benchmarks, comps and the range finder need contributor access (share a deal) or a paid plan. Without it they return 402.</li>
        <li>Each keyed request counts against a daily quota (Contributor 200, Pro 5,000, Team 50,000), reset at 00:00 UTC. See <code>x-ratelimit-remaining</code>.</li>
        <li>Errors are <code>{'{ "error": { "code", "message" } }'}</code> with a matching status: 400 invalid input, 401 invalid key, 402 access required, 429 quota or rate limit.</li>
      </ul>

      <h2>Endpoints</h2>
      {ENDPOINTS.map(([sig, text]) => (<div key={sig}><h3>{sig}</h3><p>{text}</p></div>))}

      <h2>Reading the numbers</h2>
      <ul>
        <li><b>Value</b> is total deal value in US dollars: cash plus the stated value of product or services.</li>
        <li><b>p10 … p90</b> are percentiles of that value in the cohort; <b>n</b> is the number of deals. p10 and p90 are null for cohorts under ten deals.</li>
        <li><b>cleared_rate</b> is the share of deals with an NIL Go decision that were cleared. It is null until five deals in the cohort have a decision.</li>
        <li><b>Suppression.</b> A cohort with fewer than five deals returns <code>{'{ "n", "suppressed": true }'}</code> and nothing else.</li>
        <li><b>Range finder basis.</b> If an exact match is too small, the search widens one attribute at a time — payer type, then follower range, then level, then sport — and <code>basis.widened</code> lists what was relaxed.</li>
        <li><b>Individual deals</b> are always rounded to two significant figures, with followers given as a range.</li>
      </ul>
    </div>
  );
}
