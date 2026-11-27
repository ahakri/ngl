import { useState } from 'react';
import { api } from '../api.js';
import RangeChart from '../components/RangeChart.jsx';
import { CompsTable, Field, Locked, Pick } from '../components/Bits.jsx';
import { useSession } from '../hooks.js';
import { count, fullDay, ordinal, pct, usdFull } from '../format.js';

const POSITION = {
  below: 'Below the typical range',
  within: 'Within the typical range',
  above: 'Above the typical range',
  well_above: 'Well above the typical range',
};

export default function RangeFinder() {
  const { meta, ready } = useSession();
  const [form, setForm] = useState({ sport: '', level: '', deal_type: '', payer_type: '', followers: '', amount: '' });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  if (!ready || !meta) return <div className="skeleton">Loading…</div>;
  const intro = <div><h1>Range finder</h1><p className="sub" style={{ maxWidth: 680 }}>Describe an athlete and a deal. Rangefinder finds the closest group of real deals and shows what they paid — and where a proposed amount would sit.</p></div>;
  if (!meta.abilities.rangefinder) return <div className="stack">{intro}<Locked title="Share a deal to use the range finder" /></div>;

  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v?.target ? v.target.value : v }));
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      setResult(await api.post('/v1/rangefinder', { ...form, followers: Number(form.followers), amount: form.amount === '' ? null : Number(form.amount) }));
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setBusy(false);
    }
  };
  const d = meta.dimensions;
  const s = result?.stats;

  return (
    <div className="stack">
      {intro}
      <form className="card no-print" onSubmit={submit}>
        <div className="form-grid">
          <Pick label="Sport" dim="sport" value={form.sport} onChange={set('sport')} />
          <Pick label="Competition level" dim="level" value={form.level} onChange={set('level')} />
          <Field label="Total followers" type="number" min="0" step="1" required value={form.followers} onChange={set('followers')} hint="All platforms combined" />
          <Pick label="Deal type" dim="deal_type" value={form.deal_type} onChange={set('deal_type')} />
          <Pick label="Who is paying" dim="payer_type" value={form.payer_type} onChange={set('payer_type')} />
          <Field label="Proposed amount (optional)" type="number" min="0" step="1" value={form.amount} onChange={set('amount')} hint="US dollars, cash plus in-kind" />
        </div>
        {error && <div className="notice error" style={{ marginTop: 12 }} role="alert">{error}</div>}
        <div className="row" style={{ marginTop: 14 }}><button className="btn primary" disabled={busy}>{busy ? 'Searching…' : 'Find the range'}</button></div>
      </form>

      {result && s.suppressed && (
        <div className="card"><h2>Not enough comparable deals yet</h2><p className="sub" style={{ marginTop: 6 }}>Even after widening the search there are fewer than {meta.k_min} comparable deals, so no range can be given without risking a contributor's anonymity.</p></div>
      )}

      {result && !s.suppressed && (
        <>
          <div className="card">
            <div className="row between">
              <div>
                <p className="sub">{d.sport[result.profile.sport]} · {d.level[result.profile.level]} · {d.followers[result.profile.followers_bucket]} followers · {d.deal_type[result.profile.deal_type]} · {d.payer_type[result.profile.payer_type]}</p>
                <div className="verdict" style={{ marginTop: 6 }}>
                  {result.amount === null
                    ? <>Comparable deals typically pay {usdFull(s.p25)} to {usdFull(s.p75)}.</>
                    : <>{usdFull(result.amount)} is {POSITION[result.position].toLowerCase()} — {result.percentile >= 0.995 ? 'more than every comparable deal' : result.percentile <= 0.005 ? 'less than every comparable deal' : `the ${ordinal(result.percentile)} percentile`}.</>}
                </div>
              </div>
              <button className="btn small no-print" onClick={() => window.print()}>Print report</button>
            </div>
            <div className="grid four" style={{ margin: '16px 0 4px' }}>
              <div className="tile"><div className="label">Comparable deals</div><div className="value" style={{ fontSize: 22 }}>{count(result.basis.n)}</div></div>
              <div className="tile"><div className="label">Median</div><div className="value" style={{ fontSize: 22 }}>{usdFull(s.median)}</div></div>
              <div className="tile"><div className="label">Typical range</div><div className="value" style={{ fontSize: 22 }}>{usdFull(s.p25)} – {usdFull(s.p75)}</div></div>
              <div className="tile"><div className="label">Cleared by NIL Go</div><div className="value" style={{ fontSize: 22 }}>{pct(s.cleared_rate)}</div></div>
            </div>
            <RangeChart rows={[{ key: 'cohort', label: 'Comparable deals', ...s }]} marker={result.amount === null ? null : { value: result.amount, label: `Proposed ${usdFull(result.amount)}` }} ariaLabel="Range of comparable deals" />
            <div className="notice" style={{ marginTop: 12 }}>
              <b>Basis.</b>{' '}
              {result.basis.exact_match
                ? `${count(result.basis.n)} deals matching this sport, level, follower range, deal type and payer type.`
                : `Too few exact matches, so the search was widened to include: ${result.basis.widened.join(', ')}. ${count(result.basis.n)} deals in the resulting group.`}
              {' '}Prepared {fullDay(new Date().toISOString())}. Figures are self-reported by athletes and screened for outliers; this is market context, not a determination by NIL Go or the College Sports Commission.
            </div>
          </div>
          <div className="card">
            <h2>Closest comparable deals</h2>
            <p className="sub">Nearest in value first. Amounts rounded, followers shown as a range.</p>
            <CompsTable rows={result.comps} />
          </div>
        </>
      )}
    </div>
  );
}
