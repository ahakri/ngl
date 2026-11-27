import { Link } from 'react-router-dom';
import { State } from '../components/Bits.jsx';
import { useData } from '../hooks.js';
import { fullDay } from '../format.js';

export default function Coverage() {
  const { data, loading, error } = useData('/v1/jurisdictions');
  const rows = [...(data?.data || [])].sort((a, b) => b.records - a.records);
  return (
    <div className="stack">
      <div>
        <h1>Coverage</h1>
        <p className="sub" style={{ maxWidth: 720 }}>
          Siteline currently reads the legislative record of {rows.length || '…'} city and county governments, checked daily. It does not yet cover every
          data-centre market: jurisdictions that publish through other systems, state air permits and utility-commission dockets are being added.
          If a market you need is missing, tell us.
        </p>
      </div>
      <div className="card">
        <State loading={loading} error={error}>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Jurisdiction</th><th>State</th><th className="num">Siting records</th><th>Latest activity</th><th>Last checked</th></tr></thead>
              <tbody>
                {rows.map((j) => (
                  <tr key={j.code}>
                    <td className="name"><Link to={`/records?jurisdiction=${j.code}`}>{j.name}</Link><div className="vendor">{j.kind === 'county' ? 'County' : 'City'}</div></td>
                    <td>{j.state}</td>
                    <td className="num">{j.records}</td>
                    <td>{fullDay(j.latest_activity)}</td>
                    <td>{j.last_synced ? fullDay(j.last_synced) : '—'}{!j.healthy && <span className="badge">check failed</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </State>
      </div>
    </div>
  );
}
