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
    if (key === 'contributor') return <Link className="btn" to={user ? '/submit' : '/account?next=submit'}>Share a deal</Link>;
    if (config.billing) return <button className={`btn ${key === 'pro' ? 'primary' : ''}`} disabled={busy === key} onClick={() => choose(key)}>{busy === key ? 'Redirecting…' : `Get ${config.tiers[key].name}`}</button>;
    if (config.sales_email) return <a className={`btn ${key === 'pro' ? 'primary' : ''}`} href={`mailto:${config.sales_email}?subject=Rangefinder ${config.tiers[key].name}`}>Contact sales</a>;
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
            <div className="price" style={{ marginTop: 10 }}>{t.price ? <>${t.price.toLocaleString('en-US')}<small> / month</small></> : <>Free<small> with a deal</small></>}</div>
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
        <p className="sub" style={{ maxWidth: 660 }}>Athletes pay with data, not money. Everyone who uses the benchmarks professionally subscribes, and that funds the database.</p>
      </div>
      <PlanCards />
      <div className="card">
        <h2>Questions</h2>
        <div className="stack" style={{ gap: 12, marginTop: 10 }}>
          <div><h3>Where does the data come from?</h3><p className="sub">Only from athletes, who share the terms of their own deals. Every submission is screened for outliers, unusual ones are reviewed by a person, and deals a moderator has seen proof of are marked verified.</p></div>
          <div><h3>Can an athlete be identified?</h3><p className="sub">We never collect names, schools, teams or brand names. Followers are shown as ranges, amounts are rounded, and no statistic or list is shown for a group of fewer than five deals.</p></div>
          <div><h3>Is this an official fair-market-value ruling?</h3><p className="sub">No. Rangefinder is independent market context. It is not affiliated with NIL Go or the College Sports Commission and cannot predict or replace their decisions.</p></div>
          <div><h3>Can I redistribute the data?</h3><p className="sub">Pro is for use inside your own organisation, including in reports for the athletes and clients you represent. Team adds an internal redistribution licence.</p></div>
        </div>
      </div>
    </div>
  );
}
