import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { useSession } from '../hooks.js';

export function PlanCards() {
  const { user, config } = useSession();
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(null);
  if (!config) return <div className="skeleton">Loading…</div>;

  const choose = async (plan) => {
    if (!user) return navigate(`/account?next=${plan}`);
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
    if (user?.plan === key) return <span className="btn" aria-disabled="true">Current plan</span>;
    if (key === 'free') return user ? null : <Link className="btn" to="/account">Create free account</Link>;
    if (config.billing) return <button className={`btn ${key === 'pro' ? 'primary' : ''}`} disabled={busy === key} onClick={() => choose(key)}>{busy === key ? 'Redirecting…' : `Get ${config.plans[key].name}`}</button>;
    if (config.sales_email) return <a className={`btn ${key === 'pro' ? 'primary' : ''}`} href={`mailto:${config.sales_email}?subject=Uptake ${config.plans[key].name}`}>Contact sales</a>;
    return <span className="sub">Checkout opens soon.</span>;
  };

  return (
    <>
      {error && <div className="notice error" style={{ marginBottom: 12 }}>{error}</div>}
      <div className="grid three">
        {Object.entries(config.plans).map(([key, p]) => (
          <div key={key} className={`card plan ${key === 'pro' ? 'featured' : ''}`}>
            <h3>{p.name}</h3>
            <p className="sub">{p.tagline}</p>
            <div className="price" style={{ marginTop: 10 }}>${p.price.toLocaleString('en-US')}<small> / month</small></div>
            <ul>{p.features.map((f) => <li key={f}>{f}</li>)}</ul>
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
        <p className="sub" style={{ maxWidth: 640 }}>One dataset, three depths. Every plan sees the same numbers, computed the same way — paid plans add history, coverage, exports and volume.</p>
      </div>
      <PlanCards />
      <div className="card">
        <h2>Questions</h2>
        <div className="stack" style={{ gap: 12, marginTop: 10 }}>
          <div><h3>Where does the data come from?</h3><p className="sub">Public aggregate statistics: PyPI's download logs, the npm registry's download counts, the Hugging Face Hub and Hacker News. Uptake adds cleaning, break detection, category definitions and the derived signals.</p></div>
          <div><h3>Are downloads the same as users?</h3><p className="sub">No. Downloads include CI and automated installs, so absolute numbers overstate people. That is why Uptake leads with share and growth inside a category, where the same bias applies to every competitor.</p></div>
          <div><h3>Can I redistribute the data?</h3><p className="sub">Free and Pro are for use inside your own organisation. Team includes an internal redistribution licence; talk to us about external publication.</p></div>
        </div>
      </div>
    </div>
  );
}
