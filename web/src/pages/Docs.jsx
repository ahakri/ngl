import { Link } from 'react-router-dom';

const origin = typeof window === 'undefined' ? '' : window.location.origin;

const ENDPOINTS = [
  ['GET /v1/meta', 'Categories, latest data dates, coverage, and data-quality notes (structural breaks and imputed days).'],
  ['GET /v1/signals?ecosystem=&category=', 'Every tracked project with its current signals. Both filters are optional.'],
  ['GET /v1/movers?ecosystem=pypi&direction=up&limit=10', 'Projects ranked by momentum (direction=down for the weakest). Minimum 10K downloads in 28 days.'],
  ['GET /v1/categories/{slug}?ecosystem=pypi', 'Leaderboard for one category plus its weekly market-share series.'],
  ['GET /v1/projects/{slug}?days=365', 'One project: signals per ecosystem, cleaned daily download series and weekly Hacker News attention.'],
  ['GET /v1/models?sort=trending&limit=25', 'Hugging Face models by trending, downloads or likes, with change versus the previous snapshot.'],
  ['GET /v1/models/orgs · /v1/models/tasks', 'Share of open-model downloads by publishing organisation or by task.'],
  ['GET /v1/export/signals.csv', 'All signals as CSV. Pro and Team.'],
  ['GET /v1/export/series.csv?project={slug}', 'Full daily series for one project as CSV. Pro and Team.'],
];

const FIELDS = [
  ['downloads_7d / downloads_28d', 'Downloads in the trailing 7 / 28 days ending on as_of.'],
  ['growth_7d / growth_28d / growth_12w', 'Change versus the immediately preceding window of the same length. null when history is too short or the window would cross a structural break.'],
  ['acceleration', 'growth_28d now minus growth_28d four weeks ago.'],
  ['share / share_delta_28d', 'Share of the category\'s 28-day downloads in that ecosystem, and its change in share points.'],
  ['momentum', '0–100 score: 50 + 50·tanh(1.6·growth_28d + 0.6·growth_7d + 0.5·acceleration + 8·share_delta). 50 is flat.'],
  ['rank / rank_delta_28d', 'Position in the category by 28-day downloads; positive delta means it climbed.'],
  ['breakout', 'true when growth_28d ≥ 20%, acceleration > 0, share is rising, and volume ≥ 10K.'],
];

export default function Docs() {
  return (
    <div className="docs" style={{ maxWidth: 820 }}>
      <h1>API reference</h1>
      <p style={{ marginTop: 8 }}>A read-only JSON API over the same data as this site. Create a key on your <Link to="/account">account page</Link> and send it as a bearer token.</p>
      <pre>{`curl ${origin}/v1/categories/model-sdks?ecosystem=npm \\
  -H "Authorization: Bearer upk_your_key"`}</pre>

      <h2>Authentication and limits</h2>
      <ul>
        <li>Send <code>Authorization: Bearer &lt;key&gt;</code>. Requests without a key work at free-plan depth and are rate-limited per IP.</li>
        <li>Each keyed request counts against your plan's daily quota (Free 100, Pro 10,000, Team 100,000), reset at 00:00 UTC. See <code>x-ratelimit-limit</code> and <code>x-ratelimit-remaining</code>.</li>
        <li>Errors are <code>{'{ "error": { "code", "message" } }'}</code> with a matching HTTP status: 401 invalid key, 402 plan required, 404 unknown resource, 429 quota or rate limit.</li>
      </ul>

      <h2>Endpoints</h2>
      {ENDPOINTS.map(([sig, text]) => (<div key={sig}><h3>{sig}</h3><p>{text}</p></div>))}

      <h2>Signal fields</h2>
      {FIELDS.map(([name, text]) => (<div key={name}><h3>{name}</h3><p>{text}</p></div>))}

      <h2>Methodology</h2>
      <ul>
        <li><b>Sources.</b> PyPI downloads exclude known mirrors. npm downloads come from the registry's public counts. Hugging Face figures are the Hub's trailing-30-day download counts, snapshotted daily.</li>
        <li><b>Windows.</b> All windows are multiples of seven days, so weekday seasonality cancels out.</li>
        <li><b>Structural breaks.</b> When a registry changes how it counts, every package shifts level at once. Uptake detects a step between two flat four-week levels in the ecosystem aggregate and refuses to compute growth or share across it. Breaks are confirmed four weeks after they happen and listed in <code>/v1/meta</code>.</li>
        <li><b>Outages.</b> Days on which a registry reports almost nothing are replaced with the mean of the same weekday in adjacent weeks and listed under <code>quality.imputed_days</code>.</li>
        <li><b>Interpretation.</b> Downloads include automated installs. Compare projects within a category rather than reading absolute counts as users.</li>
      </ul>
    </div>
  );
}
