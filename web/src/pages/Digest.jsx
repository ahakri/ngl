import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { State } from '../components/Bits.jsx';
import { useData, useSession } from '../hooks.js';
import { fullDay } from '../format.js';

function Signup() {
  const [email, setEmail] = useState('');
  const [state, setState] = useState(null);
  const submit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/subscribe', { email });
      setState({ ok: true, text: 'You are on the list. The digest goes out weekly.' });
      setEmail('');
    } catch (err) {
      setState({ ok: false, text: err.message });
    }
  };
  return (
    <form className="card" onSubmit={submit}>
      <h2>Get this every week</h2>
      <p className="sub">A short email each week: new moratoria, project hearings and votes. Free. Unsubscribe by replying.</p>
      <div className="row" style={{ marginTop: 12 }}>
        <input type="email" required placeholder="you@company.com" value={email} onChange={(e) => setEmail(e.target.value)} aria-label="Email address" style={{ flex: '1 1 240px' }} />
        <button className="btn primary">Subscribe</button>
      </div>
      {state && <div className={`notice ${state.ok ? '' : 'error'}`} style={{ marginTop: 10 }} role="status">{state.text}</div>}
    </form>
  );
}

export default function Digest() {
  const { meta } = useSession();
  const { data, loading, error } = useData('/v1/digest');
  const [copied, setCopied] = useState(false);
  const c = data?.counts;

  return (
    <div className="stack" style={{ maxWidth: 860 }}>
      <div>
        <h1>This week in data-centre siting</h1>
        <p className="sub">{data ? `${fullDay(data.week.start)} – ${fullDay(data.week.end)} · ` : ''}what city and county governments did about data centres in the last seven days.</p>
      </div>
      <Signup />
      <State loading={loading} error={error}>
        {data && (
          <>
            <div className="grid three">
              <div className="card tile"><div className="label">New or updated records</div><div className="value">{c.records}</div><div className="note">across {c.places} local government{c.places === 1 ? '' : 's'}</div></div>
              <div className="card tile"><div className="label">Restricting development</div><div className="value">{c.restrictive}</div><div className="note">{c.restrictive_last_12_months} in 12 months · {c.restrictive_prior_12_months} the year before</div></div>
              <div className="card tile"><div className="label">Hearings in the next 3 weeks</div><div className="value">{c.upcoming}</div><div className="note">on published agendas</div></div>
            </div>
            {!data.sections.length && <div className="card"><div className="skeleton">A quiet week: no new data-centre items in the covered governments.</div></div>}
            {data.sections.map((s) => (
              <div className="card" key={s.key}>
                <h2>{s.title}</h2>
                {s.items.map((i) => (
                  <Link to={`/record/${i.id}`} className="record" key={i.id}>
                    <div className="record-head"><span className="record-where">{i.place}</span><span className="sub">{fullDay(s.key === 'upcoming' ? i.agenda_date : i.date)}</span></div>
                    <div className="record-title">{i.headline}</div>
                    <div className="record-foot"><span className="tags"><span className="tag">{s.key === 'upcoming' ? meta?.categories[i.category] : meta?.outcomes[i.outcome]}</span>{i.restrictive && <span className="tag warn">⚠ Restrictive</span>}</span>{i.size && <span className="sub">{i.size}</span>}</div>
                  </Link>
                ))}
              </div>
            ))}
            <div className="card">
              <div className="row between"><h2>Share it</h2><button className="btn small" onClick={() => navigator.clipboard.writeText(data.markdown).then(() => setCopied(true), () => {})}>{copied ? 'Copied' : 'Copy as text'}</button></div>
              <p className="sub">The digest as plain text, for a newsletter or a post. Records from the last 30 days open in full on Pro and Team.</p>
            </div>
          </>
        )}
      </State>
    </div>
  );
}
