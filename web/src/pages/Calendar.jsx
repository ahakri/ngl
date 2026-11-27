import { RecordRow, State, Upgrade } from '../components/Bits.jsx';
import { useData, useSession } from '../hooks.js';
import { fullDay } from '../format.js';

export default function Calendar() {
  const { meta } = useSession();
  const allowed = meta?.abilities.upcoming;
  const { data, loading, error } = useData(allowed ? '/v1/upcoming' : null);
  const summary = useData(allowed === false ? '/v1/summary' : null);
  const days = new Map();
  for (const r of data?.data || []) days.set(r.agenda_date, [...(days.get(r.agenda_date) || []), r]);

  return (
    <div className="stack">
      <div><h1>Calendar</h1><p className="sub">Data-centre items on published future agendas — the hearings you can still attend, speak at or prepare for.</p></div>
      {!meta && <div className="skeleton">Loading…</div>}
      {allowed === false && <Upgrade>{summary.data ? `${summary.data.totals.upcoming_hearings} hearing${summary.data.totals.upcoming_hearings === 1 ? ' is' : 's are'} scheduled right now. ` : ''}The calendar is part of Pro and Team.</Upgrade>}
      {allowed && (
        <State loading={loading} error={error}>
          {data && !data.data.length && <div className="card"><div className="skeleton">No covered jurisdiction has a data-centre item on a future agenda right now.</div></div>}
          {[...days].map(([d, rows]) => (
            <div className="card" key={d}><h2>{fullDay(d)}</h2>{rows.map((r) => <RecordRow key={r.id} r={r} />)}</div>
          ))}
        </State>
      )}
    </div>
  );
}
