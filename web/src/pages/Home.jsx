import { Link } from 'react-router-dom';
import LineChart from '../components/LineChart.jsx';
import { SignalsTable, State } from '../components/Bits.jsx';
import { useData } from '../hooks.js';
import { SERIES, fullDay, num, pct } from '../format.js';
import { PlanCards } from './Pricing.jsx';

export function topShare(share, n = 5) {
  const order = share.series.map((s, i) => [i, s.share.at(-1) ?? 0]).sort((a, b) => b[1] - a[1]).map(([i]) => i);
  const top = order.slice(0, n).map((i, k) => ({ name: share.series[i].name, color: SERIES[k], values: share.series[i].share }));
  const rest = order.slice(n);
  if (rest.length) top.push({ name: `Other (${rest.length})`, color: 'var(--series-other)', values: share.dates.map((_, d) => rest.reduce((s, i) => s + share.series[i].share[d], 0)) });
  return top;
}

export default function Home() {
  const meta = useData('/v1/meta');
  const sdk = useData('/v1/categories/model-sdks?ecosystem=npm');
  const movers = useData('/v1/movers?ecosystem=pypi&limit=5');
  const c = meta.data?.coverage;

  return (
    <div>
      <section className="hero">
        <div className="eyebrow">AI ecosystem adoption data</div>
        <h1>See what AI developers are actually adopting — before it shows up in revenue.</h1>
        <p className="lead">
          Uptake measures real usage of model SDKs, agent frameworks, vector databases and open models, every day,
          and turns it into market share, momentum and breakout signals you can chart or pull through an API.
        </p>
        <div className="row">
          <Link to="/explore" className="btn primary">Explore the data</Link>
          <Link to="/docs" className="btn">API reference</Link>
        </div>
      </section>

      <div className="grid four" style={{ marginTop: 18 }}>
        <div className="card tile"><div className="label">Projects tracked</div><div className="value">{c ? c.projects : '—'}</div><div className="note">across {meta.data?.categories.length ?? '—'} competitive categories</div></div>
        <div className="card tile"><div className="label">Daily data points</div><div className="value">{c ? num(c.data_points) : '—'}</div><div className="note">{c ? `${c.series} series` : ' '}</div></div>
        <div className="card tile"><div className="label">Open models in panel</div><div className="value">{c ? num(c.hf_models) : '—'}</div><div className="note">top of Hugging Face by downloads</div></div>
        <div className="card tile"><div className="label">Data through</div><div className="value" style={{ fontSize: 22, paddingTop: 5 }}>{meta.data ? fullDay(meta.data.as_of.pypi) : '—'}</div><div className="note">refreshed daily</div></div>
      </div>

      <section className="section">
        <h2>Who is winning the model-provider race among JavaScript developers?</h2>
        <p className="sub">Share of trailing-28-day npm downloads across official provider SDKs. This is live data, not a mock-up.</p>
        <div className="card">
          <State loading={sdk.loading} error={sdk.error}>
            {sdk.data && <LineChart dates={sdk.data.share.dates} series={topShare(sdk.data.share, 4)} format={(v) => pct(v, 0)} ariaLabel="Model provider SDK share of npm downloads" />}
          </State>
          <div className="row between" style={{ marginTop: 8 }}>
            <span className="sub">Free plan shows 12 weeks. Paid plans include full history.</span>
            <Link to="/category/model-sdks">Open the category →</Link>
          </div>
        </div>
      </section>

      <section className="section">
        <h2>This week's fastest movers on PyPI</h2>
        <p className="sub">Ranked by momentum: a 0–100 score blending 28-day growth, the latest week, acceleration and share gained.</p>
        <div className="card">
          <State loading={movers.loading} error={movers.error}>{movers.data && <SignalsTable rows={movers.data.data} showShare={false} />}</State>
        </div>
      </section>

      <section className="section">
        <h2>Built for people who have to be right about AI</h2>
        <div className="grid three" style={{ marginTop: 14 }}>
          <div className="card"><h3>Investors</h3><p className="sub">Track adoption of public and private AI companies' developer products. Spot share shifts and breakouts weeks before they reach earnings calls or funding announcements.</p></div>
          <div className="card"><h3>AI infrastructure vendors</h3><p className="sub">Benchmark your SDK against competitors on the same scale. Know whether you are gaining share or just riding the market.</p></div>
          <div className="card"><h3>Product &amp; GTM teams</h3><p className="sub">Decide which frameworks, providers and vector stores to integrate with next, using evidence instead of social-media volume.</p></div>
        </div>
      </section>

      <section className="section">
        <h2>Data you can defend</h2>
        <div className="grid three" style={{ marginTop: 14 }}>
          <div className="card"><h3>Break-adjusted</h3><p className="sub">Registries change how they count. Uptake detects those level shifts automatically and never computes growth or share across one{meta.data?.quality.structural_breaks.length ? ` — most recently PyPI on ${fullDay(meta.data.quality.structural_breaks.at(-1).date)}` : ''}.</p></div>
          <div className="card"><h3>Seasonality-proof</h3><p className="sub">Every window is a multiple of seven days, so weekday patterns cancel. Upstream outage days are detected and imputed, and flagged in the API.</p></div>
          <div className="card"><h3>Aggregate and public</h3><p className="sub">Built only from public registry and hub statistics. No scraping of personal profiles, no user-level data, nothing you need a privacy review to buy.</p></div>
        </div>
      </section>

      <section className="section">
        <h2>Plans</h2>
        <p className="sub">Start free. Upgrade when you need full history, exports or volume.</p>
        <PlanCards />
      </section>
    </div>
  );
}
