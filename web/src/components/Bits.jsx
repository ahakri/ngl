import { Link } from 'react-router-dom';
import { count, pct, quarter, usd, usdFull } from '../format.js';
import { useSession } from '../hooks.js';

export function State({ loading, error, children }) {
  if (loading) return <div className="skeleton">Loading…</div>;
  if (error) return <div className="notice error">{error.message}</div>;
  return children;
}

/** Labelled <select> over one of the API's dimensions. */
export function Pick({ label, dim, value, onChange, any, error, hint }) {
  const { meta } = useSession();
  const options = meta?.dimensions[dim] || {};
  return (
    <label>
      {label}
      <select value={value || ''} onChange={(e) => onChange(e.target.value)}>
        <option value="">{any || 'Choose…'}</option>
        {Object.entries(options).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
      </select>
      {hint && <span className="hint">{hint}</span>}
      {error && <span className="field-error">{error}</span>}
    </label>
  );
}

export function Field({ label, error, hint, ...props }) {
  return (
    <label>
      {label}
      <input {...props} />
      {hint && <span className="hint">{hint}</span>}
      {error && <span className="field-error">{error}</span>}
    </label>
  );
}

/** Shown instead of data when the viewer has neither contributed nor subscribed. */
export function Locked({ title = 'Share a deal to see this' }) {
  const { user } = useSession();
  return (
    <div className="card" style={{ maxWidth: 640 }}>
      <h2>{title}</h2>
      <p className="sub" style={{ margin: '6px 0 14px' }}>
        Rangefinder runs on give-to-get. Athletes who anonymously share one of their own deals get full access for a year, free.
        Agents, brands, collectives and schools subscribe.
      </p>
      <div className="row">
        <Link className="btn primary" to={user ? '/submit' : '/account?next=submit'}>Share a deal</Link>
        <Link className="btn" to="/pricing">See plans</Link>
      </div>
    </div>
  );
}

export function StatsTable({ rows, label }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>{label}</th><th className="num">Deals</th><th className="num">25th</th><th className="num">Median</th><th className="num">75th</th><th className="num hide-sm">90th</th><th className="num hide-sm">Cleared</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.key}>
              <td className="name">{r.label}</td>
              <td className="num">{count(r.n)}</td>
              <td className="num">{usdFull(r.p25)}</td>
              <td className="num"><b>{usdFull(r.median)}</b></td>
              <td className="num">{usdFull(r.p75)}</td>
              <td className="num hide-sm">{usdFull(r.p90)}</td>
              <td className="num hide-sm" title="Share of deals with an NIL Go decision that were cleared">{pct(r.cleared_rate)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function CompsTable({ rows }) {
  const { meta } = useSession();
  const d = meta?.dimensions || {};
  const name = (dim, k) => d[dim]?.[k] || k;
  if (!rows.length) return <div className="skeleton">No comparable deals to list for this selection.</div>;
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th className="num">Total</th><th>Deal</th><th>Athlete</th><th>Paid by</th><th>Signed</th><th>NIL Go</th></tr></thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <td className="num"><b>{usd(r.total_usd)}</b>{r.in_kind && <div className="vendor">incl. in-kind</div>}</td>
              <td className="name">{name('deal_type', r.deal_type)}<div className="vendor">{r.deliverables} deliverable{r.deliverables === 1 ? '' : 's'}{r.duration_months ? ` · ${r.duration_months} mo` : ''}{r.exclusive ? ' · exclusive' : ''}</div></td>
              <td className="name">{name('sport', r.sport)}<div className="vendor">{name('level', r.level)} · {name('class_year', r.class_year)} · {name('followers', r.followers)} followers</div></td>
              <td className="name">{name('payer_type', r.payer_type)}<div className="vendor">{name('industry', r.industry)}</div></td>
              <td>{quarter(r.signed_quarter)}</td>
              <td>{name('clearance', r.clearance).replace(' by NIL Go', '')}{r.verified && <span className="badge hot" title="A moderator has seen proof of this deal">Verified</span>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
