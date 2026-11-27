import { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { api } from '../api.js';
import { Field, Pick } from '../components/Bits.jsx';
import { useSession } from '../hooks.js';

const BLANK = { sport: '', level: '', class_year: '', role: '', region: '', followers: '', payer_type: '', industry: '', deal_type: '', deliverables: '1', duration_months: '0', cash_usd: '', in_kind_usd: '', clearance: '', signed_quarter: '', exclusive: false, has_agent: false, attest_adult: false, attest_right: false };

function quarters(first, current) {
  const out = [];
  let [y, q] = [Number(current.slice(0, 4)), Number(current.slice(6))];
  while (`${y}-Q${q}` >= first) {
    out.push(`${y}-Q${q}`);
    q -= 1;
    if (q === 0) { q = 4; y -= 1; }
  }
  return out;
}

export default function Submit() {
  const { user, ready, meta, refresh } = useSession();
  const [form, setForm] = useState(BLANK);
  const [errors, setErrors] = useState({});
  const [failure, setFailure] = useState(null);
  const [done, setDone] = useState(null);
  const [busy, setBusy] = useState(false);

  if (!ready || !meta) return <div className="skeleton">Loading…</div>;
  if (!user) return <Navigate to="/account?next=submit" replace />;

  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v?.target ? (v.target.type === 'checkbox' ? v.target.checked : v.target.value) : v }));
  const num = (v) => (v === '' ? '' : Number(v));
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setErrors({});
    setFailure(null);
    try {
      const body = { ...form, followers: num(form.followers), deliverables: num(form.deliverables), duration_months: num(form.duration_months), cash_usd: num(form.cash_usd), in_kind_usd: num(form.in_kind_usd) };
      const { deal } = await api.post('/api/deals', body);
      await refresh();
      setDone(deal);
      setForm(BLANK);
    } catch (err) {
      setErrors(err.fields || {});
      setFailure(err.fields ? 'Check the highlighted fields.' : err.message);
    } finally {
      setBusy(false);
    }
  };

  if (done) {
    return (
      <div className="card" style={{ maxWidth: 640 }}>
        <h2>Thank you — your deal is in</h2>
        <p className="sub" style={{ margin: '6px 0 14px' }}>
          {done.status === 'approved'
            ? 'It is now part of the benchmarks, and you have full access for the next 12 months.'
            : 'It is unusual enough that a moderator will look at it before it is published. You have full access in the meantime.'}
        </p>
        <div className="row">
          <Link className="btn primary" to="/benchmarks">Explore benchmarks</Link>
          <Link className="btn" to="/range-finder">Open the range finder</Link>
          <button className="btn" onClick={() => setDone(null)}>Share another deal</button>
        </div>
      </div>
    );
  }

  return (
    <div className="stack" style={{ maxWidth: 860 }}>
      <div>
        <h1>Share a deal</h1>
        <p className="sub">About two minutes. We never ask for your name, your school or the brand, and nothing is published for groups of fewer than {meta.k_min} deals.</p>
      </div>
      <form className="stack" onSubmit={submit} noValidate>
        <div className="card">
          <h2>About you</h2>
          <div className="form-grid" style={{ marginTop: 12 }}>
            <Pick label="Sport" dim="sport" value={form.sport} onChange={set('sport')} error={errors.sport} />
            <Pick label="Competition level" dim="level" value={form.level} onChange={set('level')} error={errors.level} />
            <Pick label="Class year when signed" dim="class_year" value={form.class_year} onChange={set('class_year')} error={errors.class_year} />
            <label>Role (optional)
              <select value={form.role} onChange={set('role')}><option value="">Prefer not to say</option><option value="starter">Starter</option><option value="rotation">Rotation player</option><option value="reserve">Reserve</option></select>
            </label>
            <Pick label="Region of your school" dim="region" value={form.region} onChange={set('region')} error={errors.region} />
            <Field label="Total followers when signed" type="number" min="0" step="1" value={form.followers} onChange={set('followers')} error={errors.followers} hint="All platforms combined. Shown only as a range." />
          </div>
        </div>
        <div className="card">
          <h2>About the deal</h2>
          <div className="form-grid" style={{ marginTop: 12 }}>
            <Pick label="Who paid" dim="payer_type" value={form.payer_type} onChange={set('payer_type')} error={errors.payer_type} />
            <Pick label="Their industry" dim="industry" value={form.industry} onChange={set('industry')} error={errors.industry} />
            <Pick label="What you did" dim="deal_type" value={form.deal_type} onChange={set('deal_type')} error={errors.deal_type} />
            <Field label="Number of deliverables" type="number" min="1" step="1" value={form.deliverables} onChange={set('deliverables')} error={errors.deliverables} hint="Posts, appearances, sessions…" />
            <Field label="Cash paid (USD)" type="number" min="0" step="1" value={form.cash_usd} onChange={set('cash_usd')} error={errors.cash_usd} />
            <Field label="Value of free product or services (USD)" type="number" min="0" step="1" value={form.in_kind_usd} onChange={set('in_kind_usd')} error={errors.in_kind_usd} hint="Leave blank if none" />
            <Field label="Length in months" type="number" min="0" step="1" value={form.duration_months} onChange={set('duration_months')} error={errors.duration_months} hint="0 for a one-off" />
            <label>Quarter signed
              <select value={form.signed_quarter} onChange={set('signed_quarter')}>
                <option value="">Choose…</option>
                {quarters(meta.quarters.first, meta.quarters.current).map((q) => <option key={q} value={q}>{q.slice(5)} {q.slice(0, 4)}</option>)}
              </select>
              {errors.signed_quarter && <span className="field-error">{errors.signed_quarter}</span>}
            </label>
            <Pick label="NIL Go outcome" dim="clearance" value={form.clearance} onChange={set('clearance')} error={errors.clearance} />
          </div>
          <div className="stack" style={{ gap: 8, marginTop: 14 }}>
            <label className="check"><input type="checkbox" checked={form.exclusive} onChange={set('exclusive')} />The deal was exclusive (I could not work with competitors)</label>
            <label className="check"><input type="checkbox" checked={form.has_agent} onChange={set('has_agent')} />An agent or representative negotiated it</label>
          </div>
        </div>
        <div className="card">
          <h2>Confirm</h2>
          <div className="stack" style={{ gap: 10, marginTop: 12 }}>
            <label className="check"><input type="checkbox" checked={form.attest_adult} onChange={set('attest_adult')} /><span>I am 18 or older.{errors.attest_adult && <span className="field-error"> {errors.attest_adult}</span>}</span></label>
            <label className="check"><input type="checkbox" checked={form.attest_right} onChange={set('attest_right')} /><span>This is my own deal, the details are accurate, and sharing these terms anonymously does not break a confidentiality clause in my contract.{errors.attest_right && <span className="field-error"> {errors.attest_right}</span>}</span></label>
          </div>
          {failure && <div className="notice error" style={{ marginTop: 12 }} role="alert">{failure}</div>}
          <div className="row" style={{ marginTop: 14 }}><button className="btn primary" disabled={busy}>{busy ? 'Submitting…' : 'Submit deal'}</button></div>
        </div>
      </form>
    </div>
  );
}
