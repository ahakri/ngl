import { Link } from 'react-router-dom';
import { CATEGORY_COLOR, fullDay, size } from '../format.js';
import { useSession } from '../hooks.js';

export function State({ loading, error, children }) {
  if (loading) return <div className="skeleton">Loading…</div>;
  if (error) return <div className="notice error">{error.message}</div>;
  return children;
}

export function Upgrade({ children }) {
  return (
    <div className="notice lock">
      <span>{children}</span>
      <Link className="btn small primary" to="/pricing">See plans</Link>
    </div>
  );
}

const OUTCOME_ICON = { approved: '✓', denied: '✕', continued: '↻', pending: '•', withdrawn: '–' };

export function Tags({ r }) {
  const { meta } = useSession();
  return (
    <span className="tags">
      <span className="tag"><i style={{ background: CATEGORY_COLOR[r.category] }} />{meta?.categories[r.category] || r.category}</span>
      <span className={`tag outcome-${r.outcome}`}>{OUTCOME_ICON[r.outcome]} {meta?.outcomes[r.outcome] || r.outcome}</span>
      {r.restrictive && <span className="tag warn">⚠ Restrictive</span>}
    </span>
  );
}

/** One siting record as a list row. */
export function RecordRow({ r }) {
  const title = r.project_name || r.title.replace(/\s+/g, ' ');
  return (
    <Link to={`/record/${r.id}`} className="record">
      <div className="record-head">
        <span className="record-where">{r.jurisdiction.name}, {r.jurisdiction.state}</span>
        <span className="sub">{fullDay(r.event_date)}</span>
      </div>
      <div className="record-title">{title.length > 150 ? `${title.slice(0, 150)}…` : title}</div>
      {r.project_name && <div className="sub clamp">{r.title.replace(/\s+/g, ' ')}</div>}
      <div className="record-foot"><Tags r={r} />{size(r) && <span className="sub">{size(r)}</span>}</div>
    </Link>
  );
}
