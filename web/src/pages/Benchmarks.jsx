import { useState } from 'react';
import RangeChart from '../components/RangeChart.jsx';
import { CompsTable, Locked, Pick, State, StatsTable } from '../components/Bits.jsx';
import { useData, useSession } from '../hooks.js';
import { count, pct, usdFull } from '../format.js';

const GROUPS = [['sport', 'Sport'], ['level', 'Competition level'], ['followers', 'Follower range'], ['deal_type', 'Deal type'], ['payer_type', 'Who paid'], ['industry', 'Industry'], ['class_year', 'Class year'], ['region', 'Region'], ['quarter', 'Quarter signed']];
const FILTERS = [['sport', 'Sport'], ['level', 'Level'], ['followers', 'Followers'], ['deal_type', 'Deal type'], ['payer_type', 'Who paid']];

export default function Benchmarks() {
  const { meta, ready } = useSession();
  const [filters, setFilters] = useState({});
  const [group, setGroup] = useState('sport');
  const allowed = meta?.abilities.explorer;
  const qs = new URLSearchParams({ ...filters, group_by: group }).toString();
  const bench = useData(allowed ? `/v1/benchmarks?${qs}` : null);
  const comps = useData(allowed ? `/v1/comps?${new URLSearchParams(filters)}` : null);

  if (!ready || !meta) return <div className="skeleton">Loading…</div>;
  if (!allowed) return <div className="stack"><div><h1>Benchmarks</h1><p className="sub">What NIL deals pay, by sport, level, audience, deal type and payer.</p></div><Locked /></div>;

  const set = (dim) => (v) => setFilters((f) => {
    const next = { ...f, [dim]: v };
    if (!v) delete next[dim];
    return next;
  });
  const o = bench.data?.overall;
  const groupLabel = GROUPS.find(([k]) => k === group)[1];

  return (
    <div className="stack">
      <div className="row between">
        <div><h1>Benchmarks</h1><p className="sub">Total value per deal, cash plus in-kind. Every figure covers at least {meta.k_min} deals.</p></div>
        {meta.abilities.export && <a className="btn small" href={`/v1/export/benchmarks.csv?${qs}`}>Download CSV</a>}
      </div>

      <div className="card">
        <div className="filters">
          {FILTERS.map(([dim, label]) => <Pick key={dim} label={label} dim={dim} value={filters[dim]} onChange={set(dim)} any="All" />)}
          <label>Break down by
            <select value={group} onChange={(e) => setGroup(e.target.value)}>{GROUPS.map(([k, l]) => <option key={k} value={k}>{l}</option>)}</select>
          </label>
        </div>
      </div>

      <State loading={bench.loading && !bench.data} error={bench.error}>
        {o && (o.suppressed ? (
          <div className="card"><h2>Not enough deals yet</h2><p className="sub" style={{ marginTop: 6 }}>{o.n === 0 ? 'No deals match' : `Only ${o.n} deal${o.n === 1 ? ' matches' : 's match'}`} this selection. Figures appear once there are {meta.k_min}, so no contributor can be singled out. Try removing a filter.</p></div>
        ) : (
          <>
            <div className="grid four">
              <div className="card tile"><div className="label">Deals in selection</div><div className="value">{count(o.n)}</div><div className="note">{pct(o.verified_share)} verified</div></div>
              <div className="card tile"><div className="label">Median</div><div className="value">{usdFull(o.median)}</div><div className="note">half of deals pay more</div></div>
              <div className="card tile"><div className="label">Typical range</div><div className="value" style={{ fontSize: 21, paddingTop: 5 }}>{usdFull(o.p25)} – {usdFull(o.p75)}</div><div className="note">middle half of deals</div></div>
              <div className="card tile"><div className="label">Cleared by NIL Go</div><div className="value">{pct(o.cleared_rate)}</div><div className="note">of deals with a decision</div></div>
            </div>
            <div className="card">
              <h2>By {groupLabel.toLowerCase()}</h2>
              <p className="sub">{bench.data.rows.length ? 'Groups with fewer than five deals are left out.' : 'No group in this breakdown has five deals yet.'}</p>
              {bench.data.rows.length > 0 && (
                <>
                  <RangeChart rows={bench.data.rows.slice(0, 14)} ariaLabel={`Deal value by ${groupLabel}`} />
                  <div style={{ marginTop: 14 }}><StatsTable rows={bench.data.rows} label={groupLabel} /></div>
                </>
              )}
            </div>
            <div className="card">
              <h2>Recent comparable deals</h2>
              <p className="sub">Amounts are rounded and followers shown as a range. {comps.data && comps.data.n > comps.data.rows.length ? `Showing ${comps.data.rows.length} of ${count(comps.data.n)}.` : ''}</p>
              <State loading={comps.loading && !comps.data} error={comps.error}>{comps.data && <CompsTable rows={comps.data.rows} />}</State>
            </div>
          </>
        ))}
      </State>
    </div>
  );
}
