import { Link, useParams } from 'react-router-dom';
import { State, Tags, Upgrade } from '../components/Bits.jsx';
import { useData } from '../hooks.js';
import { compact, count, fullDay } from '../format.js';

const Fact = ({ label, children }) => (children ? <div className="fact"><div className="label">{label}</div><div className="v">{children}</div></div> : null);

export default function RecordDetail() {
  const { id } = useParams();
  const { data: r, loading, error } = useData(`/v1/records/${id}`);
  if (error?.status === 402) return <div className="stack"><h1>Record #{id}</h1><Upgrade>{error.message}</Upgrade></div>;

  return (
    <State loading={loading} error={error}>
      {r && (
        <div className="stack">
          <div>
            <p className="sub"><Link to="/records">Records</Link> / <Link to={`/records?jurisdiction=${r.jurisdiction.code}`}>{r.jurisdiction.name}, {r.jurisdiction.state}</Link></p>
            <h1>{r.project_name || `${r.jurisdiction.name}: ${r.item_type || 'Agenda item'}`}</h1>
            <div style={{ marginTop: 8 }}><Tags r={r} /></div>
          </div>
          <div className="card">
            <div className="facts">
              <Fact label="Latest activity">{fullDay(r.event_date)}</Fact>
              <Fact label="Site area">{r.acres && `${count(r.acres)} acres`}</Fact>
              <Fact label="Building area">{r.square_feet && `${compact(r.square_feet)} sq ft`}</Fact>
              <Fact label="Power">{r.mw && `${count(r.mw)} MW`}</Fact>
              <Fact label="Case number">{r.case_number}</Fact>
              <Fact label="File">{r.file}</Fact>
              <Fact label="Heard by">{r.body}</Fact>
              <Fact label="Local status">{r.local_status}</Fact>
              <Fact label="Staff recommendation">{r.staff_recommendation}</Fact>
              <Fact label="Next agenda">{r.agenda_date && r.agenda_date >= new Date().toISOString().slice(0, 10) ? fullDay(r.agenda_date) : null}</Fact>
            </div>
          </div>
          <div className="card">
            <div className="row between"><h2>Official text</h2><a className="btn small" href={r.source_url} target="_blank" rel="noreferrer">Open the source record ↗</a></div>
            <p className="original" style={{ marginTop: 10 }}>{r.title}</p>
          </div>
          <div className="card">
            <h2>Action history</h2>
            {r.actions.length ? (
              <ul className="timeline">
                {r.actions.map((a, i) => (
                  <li key={i}><b>{fullDay(a.date)}</b> · {a.body || 'Body not recorded'}<div className="sub">{[a.action, a.result, a.tally].filter(Boolean).join(' · ') || 'No action recorded'}</div></li>
                ))}
              </ul>
            ) : <p className="sub" style={{ marginTop: 6 }}>No votes or actions have been recorded on this item yet.</p>}
          </div>
          <p className="sub">Type, size and outcome are derived from the official text by rule and can be wrong; the source record is authoritative.</p>
        </div>
      )}
    </State>
  );
}
