import { useEffect, useState } from 'react';
import { api } from '../api.js';
import { useSession } from '../hooks.js';
import { count, fullDay, quarter, usdFull } from '../format.js';

export default function Admin() {
  const { me, meta, ready } = useSession();
  const [queue, setQueue] = useState(null);
  const [error, setError] = useState(null);
  const load = () => api.get('/api/admin/queue').then((r) => setQueue(r.deals), (e) => setError(e.message));
  useEffect(() => { if (me?.is_admin) load(); }, [me?.is_admin]);

  if (!ready || !meta) return <div className="skeleton">Loading…</div>;
  if (!me?.is_admin) return <div className="card"><h2>Moderators only</h2></div>;
  const act = (id, action) => api.post(`/api/admin/deals/${id}`, { action }).then(load, (e) => setError(e.message));
  const d = meta.dimensions;

  return (
    <div className="stack">
      <div><h1>Review queue</h1><p className="sub">Submissions held back by screening. Approve what is plausible, verify what you have seen proof of, reject the rest.</p></div>
      {error && <div className="notice error">{error}</div>}
      {queue && !queue.length && <div className="card"><div className="skeleton">Nothing waiting.</div></div>}
      {(queue || []).map((q) => (
        <div className="card" key={q.id}>
          <div className="row between">
            <h2>{usdFull(q.total_usd)} <span className="sub">· {d.deal_type[q.deal_type]} · {d.payer_type[q.payer_type]}</span></h2>
            <span className="sub">#{q.id} · {fullDay(q.created_at)}</span>
          </div>
          <p className="sub" style={{ margin: '6px 0' }}>
            {d.sport[q.sport]} · {d.level[q.level]} · {d.class_year[q.class_year]} · {count(q.followers)} followers · {d.region[q.region]} · {d.industry[q.industry]} ·
            {' '}{usdFull(q.cash_usd)} cash + {usdFull(q.in_kind_usd)} in kind · {q.deliverables} deliverable(s) · {q.duration_months} mo · signed {quarter(q.signed_quarter)} · {d.clearance[q.clearance]}
          </p>
          <ul style={{ margin: '6px 0 12px', paddingLeft: 18 }}>{q.flags.map((f) => <li key={f}>{f}</li>)}{!q.flags.length && <li>Held because automatic approval is off.</li>}</ul>
          <div className="row">
            <button className="btn primary small" onClick={() => act(q.id, 'approve')}>Approve</button>
            <button className="btn small" onClick={() => act(q.id, 'verify')}>Approve and mark verified</button>
            <button className="btn small" onClick={() => act(q.id, 'reject')}>Reject</button>
          </div>
        </div>
      ))}
    </div>
  );
}
