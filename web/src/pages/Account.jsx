import { useState } from 'react';
import { Link, Navigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useSession } from '../hooks.js';
import { fullDay, quarter, usdFull } from '../format.js';

function AuthForm() {
  const { refresh } = useSession();
  const [mode, setMode] = useState('signup');
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api.post(`/api/auth/${mode}`, form);
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };
  const field = (k) => ({ value: form[k], onChange: (e) => setForm({ ...form, [k]: e.target.value }) });
  return (
    <div className="card" style={{ maxWidth: 440 }}>
      <h2>{mode === 'signup' ? 'Create your account' : 'Sign in'}</h2>
      <p className="sub" style={{ marginBottom: 14 }}>{mode === 'signup' ? 'Free, no card needed. Your email is never shown to anyone.' : 'Welcome back.'}</p>
      <form className="auth" onSubmit={submit}>
        <label>Email<input type="email" autoComplete="email" required {...field('email')} /></label>
        <label>Password<input type="password" autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} minLength={10} required {...field('password')} /></label>
        {error && <div className="notice error" role="alert">{error}</div>}
        <button className="btn primary" disabled={busy}>{busy ? 'Working…' : mode === 'signup' ? 'Create account' : 'Sign in'}</button>
        {mode === 'signup' && <p className="sub">By creating an account you agree to the <Link to="/terms">Terms</Link> and <Link to="/privacy">Privacy Policy</Link>.</p>}
      </form>
      <p className="sub" style={{ marginTop: 12 }}>
        {mode === 'signup' ? 'Already have an account? ' : 'New here? '}
        <button className="btn small" onClick={() => { setMode(mode === 'signup' ? 'login' : 'signup'); setError(null); }}>{mode === 'signup' ? 'Sign in' : 'Create one'}</button>
      </p>
    </div>
  );
}

function PasswordCard() {
  const [form, setForm] = useState({ current: '', next: '' });
  const [msg, setMsg] = useState(null);
  const submit = async (e) => {
    e.preventDefault();
    setMsg(null);
    try {
      await api.post('/api/auth/password', form);
      setForm({ current: '', next: '' });
      setMsg({ ok: true, text: 'Password changed. Other devices have been signed out.' });
    } catch (err) {
      setMsg({ ok: false, text: err.message });
    }
  };
  const field = (k) => ({ value: form[k], onChange: (e) => setForm({ ...form, [k]: e.target.value }) });
  return (
    <div className="card">
      <h2>Password</h2>
      <form className="auth" style={{ marginTop: 12 }} onSubmit={submit}>
        <label>Current password<input type="password" autoComplete="current-password" required {...field('current')} /></label>
        <label>New password<input type="password" autoComplete="new-password" minLength={10} required {...field('next')} /></label>
        {msg && <div className={`notice ${msg.ok ? '' : 'error'}`} role="status">{msg.text}</div>}
        <button className="btn">Change password</button>
      </form>
    </div>
  );
}

export default function Account() {
  const { user, me, meta, ready, config, refresh } = useSession();
  const [params] = useSearchParams();
  const [fresh, setFresh] = useState(null);
  const [name, setName] = useState('');
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  if (!ready) return <div className="skeleton">Loading…</div>;
  if (!user) return <AuthForm />;
  if (params.get('next') === 'submit') return <Navigate to="/submit" replace />;
  if (!me) return <div className="skeleton">Loading…</div>;

  const run = async (fn) => {
    setError(null);
    try {
      await fn();
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  };
  const createKey = (e) => {
    e.preventDefault();
    run(async () => {
      setFresh((await api.post('/api/keys', { name })).key);
      setCopied(false);
      setName('');
    });
  };
  const today = me.usage.find((u) => u.date === new Date().toISOString().slice(0, 10))?.requests || 0;

  return (
    <div className="stack">
      <div className="row between">
        <div><h1>Account</h1><p className="sub">{user.email}</p></div>
        <button className="btn" onClick={() => run(() => api.post('/api/auth/logout'))}>Sign out</button>
      </div>
      {params.get('upgraded') && <div className="notice">Payment received — your access updates as soon as Stripe confirms it, usually within a few seconds.</div>}
      {error && <div className="notice error" role="alert">{error}</div>}

      <div className="grid three">
        <div className="card tile"><div className="label">Access</div><div className="value">{me.tier_name}</div>
          <div className="note">{me.tier === 'free' ? <><Link to="/submit">Share a deal</Link> or <Link to="/pricing">subscribe</Link> to unlock the data</> : me.tier === 'contributor' ? 'Unlocked by sharing a deal' : user.has_subscription && config?.billing ? <button className="btn small" onClick={() => run(async () => window.location.assign((await api.post('/api/billing/portal')).url))}>Manage billing</button> : 'Active subscription'}</div></div>
        <div className="card tile"><div className="label">API requests today</div><div className="value">{today.toLocaleString('en-US')}</div><div className="note">of {me.limits.daily_requests.toLocaleString('en-US')} per day</div></div>
        <div className="card tile"><div className="label">Deals shared</div><div className="value">{me.deals.length}</div><div className="note">{me.limits.export ? 'CSV export included' : 'CSV export on Pro and Team'}</div></div>
      </div>

      <div className="card">
        <div className="row between"><h2>Your deals</h2><Link className="btn small primary" to="/submit">Share a deal</Link></div>
        <p className="sub">Only you can see this list. Withdrawing a deal deletes it; if it was your only one, contributor access ends.</p>
        {me.deals.length ? (
          <div className="table-wrap" style={{ marginTop: 8 }}>
            <table>
              <thead><tr><th>Deal</th><th className="num">Total</th><th>Signed</th><th>Status</th><th /></tr></thead>
              <tbody>
                {me.deals.map((d) => (
                  <tr key={d.id}>
                    <td className="name">{meta?.dimensions.deal_type[d.deal_type]}<div className="vendor">{meta?.dimensions.sport[d.sport]} · {meta?.dimensions.payer_type[d.payer_type]}</div></td>
                    <td className="num">{usdFull(d.total_usd)}</td>
                    <td>{quarter(d.signed_quarter)}</td>
                    <td><span className="status">{d.status === 'approved' ? (d.verified ? 'Published · verified' : 'Published') : d.status === 'pending' ? 'In review' : 'Not accepted'}</span></td>
                    <td className="num"><button className="btn small" onClick={() => { if (window.confirm('Withdraw this deal? It will be deleted from the database.')) run(() => api.del(`/api/deals/${d.id}`)); }}>Withdraw</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <p className="sub" style={{ marginTop: 8 }}>You have not shared a deal yet.</p>}
      </div>

      <div className="card">
        <h2>API keys</h2>
        <p className="sub">Keys are shown once, when created. Store them somewhere safe. See the <Link to="/docs">API reference</Link>.</p>
        {fresh && (
          <div className="notice" style={{ marginTop: 12 }}>
            <div className="row between"><b>New key “{fresh.name}” — copy it now:</b>
              <button className="btn small" onClick={() => navigator.clipboard.writeText(fresh.key).then(() => setCopied(true), () => {})}>{copied ? 'Copied' : 'Copy'}</button></div>
            <div className="keybox" style={{ marginTop: 6 }}>{fresh.key}</div>
          </div>
        )}
        <form className="row" style={{ margin: '14px 0' }} onSubmit={createKey}>
          <input placeholder="Key name, e.g. research notebook" value={name} onChange={(e) => setName(e.target.value)} maxLength={60} style={{ flex: '1 1 220px' }} aria-label="Key name" />
          <button className="btn primary">Create key</button>
        </form>
        {me.keys.length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Name</th><th>Key</th><th>Created</th><th>Last used</th><th /></tr></thead>
              <tbody>
                {me.keys.map((k) => (
                  <tr key={k.id}>
                    <td>{k.name}</td><td className="mono">{k.prefix}…</td><td>{fullDay(k.created_at)}</td><td>{k.last_used_at ? fullDay(k.last_used_at) : <span className="muted">Never</span>}</td>
                    <td className="num"><button className="btn small" onClick={() => { if (window.confirm(`Revoke key “${k.name}”? Anything using it will stop working.`)) run(() => api.del(`/api/keys/${k.id}`)); }}>Revoke</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <p className="sub">No keys yet.</p>}
      </div>
      <PasswordCard />
    </div>
  );
}
