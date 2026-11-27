import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useSession } from '../hooks.js';
import { fullDay } from '../format.js';

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
      <p className="sub" style={{ marginBottom: 14 }}>{mode === 'signup' ? 'Free plan, no card needed. You get an API key straight away.' : 'Welcome back.'}</p>
      <form className="auth" onSubmit={submit}>
        <label>Email<input type="email" autoComplete="email" required {...field('email')} /></label>
        <label>Password<input type="password" autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} minLength={10} required {...field('password')} /></label>
        {error && <div className="notice error" role="alert">{error}</div>}
        <button className="btn primary" disabled={busy}>{busy ? 'Working…' : mode === 'signup' ? 'Create account' : 'Sign in'}</button>
      </form>
      <p className="sub" style={{ marginTop: 12 }}>
        {mode === 'signup' ? 'Already have an account? ' : 'New here? '}
        <button className="btn small" onClick={() => { setMode(mode === 'signup' ? 'login' : 'signup'); setError(null); }}>{mode === 'signup' ? 'Sign in' : 'Create one'}</button>
      </p>
    </div>
  );
}

export default function Account() {
  const { user, me, ready, config, refresh } = useSession();
  const [params] = useSearchParams();
  const [fresh, setFresh] = useState(null);
  const [name, setName] = useState('');
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  if (!ready) return <div className="skeleton">Loading…</div>;
  if (!user) return <AuthForm />;

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
      {params.get('upgraded') && <div className="notice">Payment received — your plan updates as soon as Stripe confirms it, usually within a few seconds.</div>}
      {params.get('next') && user.plan === 'free' && <div className="notice lock"><span>You're signed in. Continue to choose a plan.</span><Link className="btn small primary" to="/pricing">Choose plan</Link></div>}
      {error && <div className="notice error" role="alert">{error}</div>}

      <div className="grid three">
        <div className="card tile"><div className="label">Plan</div><div className="value">{config?.plans[user.plan]?.name || user.plan}</div>
          <div className="note">{user.plan === 'free' ? <Link to="/pricing">Upgrade</Link> : user.has_subscription && config?.billing ? <button className="btn small" onClick={() => run(async () => window.location.assign((await api.post('/api/billing/portal')).url))}>Manage billing</button> : 'Active'}</div></div>
        <div className="card tile"><div className="label">API requests today</div><div className="value">{today.toLocaleString('en-US')}</div><div className="note">of {me.limits.daily_requests.toLocaleString('en-US')} per day</div></div>
        <div className="card tile"><div className="label">History</div><div className="value">{me.limits.history_days > 1000 ? 'Full' : `${me.limits.history_days} days`}</div><div className="note">{me.limits.export ? 'CSV export included' : 'CSV export on Pro and Team'}</div></div>
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
    </div>
  );
}
