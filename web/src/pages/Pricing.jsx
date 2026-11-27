import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { useSession } from '../hooks.js';

export function PlanCards() {
  const { user, me, config } = useSession();
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(null);
  if (!config) return <div className="skeleton">Loading…</div>;

  const choose = async (plan) => {
    if (!user) return navigate(`/account?next=pricing`);
    setBusy(plan);
    setError(null);
    try {
      window.location.assign((await api.post('/api/billing/checkout', { plan })).url);
    } catch (err) {
      setError(err.message);
      setBusy(null);
    }
    return undefined;
  };

  const action = (key) => {
    if (me?.tier === key) return <span className="btn" aria-disabled="true">Your current access</span>;
    if (key === 'free') return user ? null : <Link className="btn" to="/account">Create free account</Link>;
    if (config.billing) return <button className={`btn ${key === 'pro' ? 'primary' : ''}`} disabled={busy === key} onClick={() => choose(key)}>{busy === key ? 'Redirecting…' : `Get ${config.tiers[key].name}`}</button>;
    if (config.sales_email) return <a className={`btn ${key === 'pro' ? 'primary' : ''}`} href={`mailto:${config.sales_email}?subject=Siteline ${config.tiers[key].name}`}>Contact sales</a>;
    return <span className="sub">Checkout opens soon.</span>;
  };

  return (
    <>
      {error && <div className="notice error" style={{ marginBottom: 12 }}>{error}</div>}
      <div className="grid three">
        {Object.entries(config.tiers).map(([key, t]) => (
          <div key={key} className={`card plan ${key === 'pro' ? 'featured' : ''}`}>
            <h3>{t.name}</h3>
            <p className="sub">{t.tagline}</p>
            <div className="price" style={{ marginTop: 10 }}>${t.price.toLocaleString('en-US')}<small> / month</small></div>
            <ul>{t.features.map((f) => <li key={f}>{f}</li>)}</ul>
            {action(key)}
          </div>
        ))}
      </div>
    </>
  );
}

export default function Pricing() {
  return (
    <div className="stack">
      <div>
        <h1>Pricing</h1>
        <p className="sub" style={{ maxWidth: 660 }}>The same records on every plan. Free runs 30 days behind; paid plans are live and add the hearing calendar, alerts, export and API volume.</p>
      </div>
      <PlanCards />
      <div className="card">
        <h2>Questions</h2>
        <div className="stack" style={{ gap: 12, marginTop: 10 }}>
          <div><h3>Where does the data come from?</h3><p className="sub">The official legislative record of each covered city and county: agendas, ordinances, zoning cases and the votes on them. Every record links back to its source page.</p></div>
          <div><h3>How current is it?</h3><p className="sub">Every jurisdiction is checked daily. Items usually appear when the agenda is published, typically one to two weeks before the hearing.</p></div>
          <div><h3>How are records classified?</h3><p className="sub">By rule, from the official text: project entitlement, policy, incentive, or power and water. Size figures are extracted the same way. It is not perfect, which is why the original text and source link are always shown.</p></div>
          <div><h3>What is not covered yet?</h3><p className="sub">Governments that publish through other agenda systems, state air permits for on-site generation, and utility-commission dockets. See the <Link to="/coverage">coverage page</Link> for exactly what is in.</p></div>
        </div>
      </div>
    </div>
  );
}
