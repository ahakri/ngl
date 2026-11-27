import { Link } from 'react-router-dom';
import { ECO_LABEL, num, pct, points, signedPct, tone } from '../format.js';
import { useSession } from '../hooks.js';

export function EcoToggle({ value, onChange, options = ['pypi', 'npm'] }) {
  return (
    <div className="seg" role="group" aria-label="Ecosystem">
      {options.map((e) => (
        <button key={e} className={value === e ? 'on' : ''} onClick={() => onChange(e)} aria-pressed={value === e}>{ECO_LABEL[e]}</button>
      ))}
    </div>
  );
}

export const Delta = ({ v, fmt = signedPct }) => <span className={tone(v)}>{fmt(v)}</span>;

export function Momentum({ v }) {
  if (v === null || v === undefined) return <span className="muted" title="Not enough comparable history">—</span>;
  return (
    <span title="Momentum score, 0–100. 50 is flat.">
      <span className="meter" aria-hidden="true"><i style={{ width: `${v}%` }} /></span>
      {v.toFixed(0)}
    </span>
  );
}

/** The core table: one row per project with its adoption signals. */
export function SignalsTable({ rows, showRank = false, showShare = true }) {
  if (!rows.length) return <div className="skeleton">No data for this view yet.</div>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {showRank && <th className="num">#</th>}
            <th>Project</th>
            <th className="num">Downloads, 28d</th>
            <th className="num">7d</th>
            <th className="num">28d</th>
            {showShare && <th className="num">Share</th>}
            {showShare && <th className="num hide-sm">Share Δ 28d</th>}
            <th className="num">Momentum</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={`${r.project}-${r.ecosystem}`}>
              {showRank && (
                <td className="num">
                  {r.rank}
                  {r.rank_delta_28d ? <span className={r.rank_delta_28d > 0 ? 'up' : 'down'} title={`${Math.abs(r.rank_delta_28d)} place(s) vs 28 days ago`}> {r.rank_delta_28d > 0 ? '▲' : '▼'}</span> : null}
                </td>
              )}
              <td className="name">
                <Link to={`/project/${r.project}`}>{r.name}</Link>
                {r.breakout && <span className="badge hot" title="Growing ≥20% over 28 days, accelerating, and gaining share">Breakout</span>}
                <div className="vendor">{r.vendor} · <span className="mono">{r.package}</span></div>
              </td>
              <td className="num">{num(r.downloads_28d)}</td>
              <td className="num"><Delta v={r.growth_7d} /></td>
              <td className="num"><Delta v={r.growth_28d} /></td>
              {showShare && <td className="num">{pct(r.share)}</td>}
              {showShare && <td className="num hide-sm"><Delta v={r.share_delta_28d} fmt={points} /></td>}
              <td className="num"><Momentum v={r.momentum} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function UpgradeNotice({ children }) {
  const { user } = useSession();
  if (user && user.plan !== 'free') return null;
  return (
    <div className="notice lock">
      <span>{children}</span>
      <Link className="btn small primary" to="/pricing">See plans</Link>
    </div>
  );
}

export function State({ loading, error, children }) {
  if (loading) return <div className="skeleton">Loading…</div>;
  if (error) return <div className="notice error">{error.message}</div>;
  return children;
}

/** Horizontal bars with direct value labels — for ranked share lists. */
export function BarList({ rows, max }) {
  const top = max ?? Math.max(...rows.map((r) => r.value), 0);
  return (
    <div style={{ display: 'grid', gap: 6 }}>
      {rows.map((r) => (
        <div key={r.label} title={`${r.label}: ${r.display}`} style={{ display: 'grid', gridTemplateColumns: 'minmax(90px, 34%) 1fr 64px', gap: 10, alignItems: 'center', fontSize: 13.5 }}>
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.label}</span>
          <span style={{ height: 14, display: 'block' }}>
            <i style={{ display: 'block', height: '100%', width: `${Math.max(0.6, (r.value / top) * 100)}%`, background: 'var(--series-1)', borderRadius: '0 4px 4px 0' }} />
          </span>
          <span style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{r.display}</span>
        </div>
      ))}
    </div>
  );
}
