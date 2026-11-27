import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { RecordRow, State, Upgrade } from '../components/Bits.jsx';
import { useData, useSession } from '../hooks.js';
import { count } from '../format.js';

const PAGE = 25;

export default function Records() {
  const { meta, user, refresh } = useSession();
  const [params, setParams] = useSearchParams();
  const [saved, setSaved] = useState(null);
  const cov = useData('/v1/jurisdictions');
  const filters = Object.fromEntries(['state', 'jurisdiction', 'category', 'outcome', 'restrictive', 'q'].map((k) => [k, params.get(k) || '']).filter(([, v]) => v));
  const offset = Number(params.get('offset')) || 0;
  const qs = new URLSearchParams({ ...filters, limit: PAGE, offset }).toString();
  const { data, loading, error } = useData(`/v1/records?${qs}`);

  const set = (k, v) => {
    const next = { ...filters, [k]: v };
    if (!v) delete next[k];
    if (k === 'state') delete next.jurisdiction;
    setParams(next);
    setSaved(null);
  };
  const saveWatch = async () => {
    const name = window.prompt('Name this watch', Object.values(filters).join(' · ') || 'All records');
    if (!name) return;
    try {
      const { watch } = await api.post('/api/watches', { name, filters });
      await refresh();
      setSaved({ ok: true, text: `Saved. Private feed: ${watch.feed_url}` });
    } catch (err) {
      setSaved({ ok: false, text: err.message });
    }
  };
  const places = (cov.data?.data || []).filter((j) => !filters.state || j.state === filters.state);

  return (
    <div className="stack">
      <div className="row between">
        <div><h1>Records</h1><p className="sub">Agenda items and legislation that affect where data centres can be built.</p></div>
        <div className="row">
          {meta?.abilities.export && <a className="btn small" href={`/v1/export/records.csv?${new URLSearchParams(filters)}`}>Download CSV</a>}
          {user && meta?.abilities.watches > 0 && <button className="btn small" onClick={saveWatch}>Save as watch</button>}
        </div>
      </div>

      <div className="card">
        <div className="filters">
          <label>State<select value={filters.state || ''} onChange={(e) => set('state', e.target.value)}><option value="">All</option>{meta?.states.map((s) => <option key={s}>{s}</option>)}</select></label>
          <label>Jurisdiction<select value={filters.jurisdiction || ''} onChange={(e) => set('jurisdiction', e.target.value)}><option value="">All</option>{places.map((j) => <option key={j.code} value={j.code}>{j.name}, {j.state}</option>)}</select></label>
          <label>Type<select value={filters.category || ''} onChange={(e) => set('category', e.target.value)}><option value="">All</option>{Object.entries(meta?.categories || {}).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label>
          <label>Outcome<select value={filters.outcome || ''} onChange={(e) => set('outcome', e.target.value)}><option value="">All</option>{Object.entries(meta?.outcomes || {}).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label>
          <label>Search<input type="search" defaultValue={filters.q || ''} placeholder="Project, company, keyword" onKeyDown={(e) => e.key === 'Enter' && set('q', e.currentTarget.value.trim())} onBlur={(e) => e.target.value.trim() !== (filters.q || '') && set('q', e.target.value.trim())} /></label>
          <label className="check" style={{ alignSelf: 'end', paddingBottom: 9 }}><input type="checkbox" checked={Boolean(filters.restrictive)} onChange={(e) => set('restrictive', e.target.checked ? '1' : '')} />Restrictive only</label>
        </div>
      </div>

      {saved && <div className={`notice ${saved.ok ? '' : 'error'}`} style={{ wordBreak: 'break-all' }}>{saved.text}</div>}
      {data?.withheld_by_plan > 0 && <Upgrade>{count(data.withheld_by_plan)} newer record{data.withheld_by_plan === 1 ? '' : 's'} from the last {data.embargo_days} days {data.withheld_by_plan === 1 ? 'is' : 'are'} live on Pro and Team.</Upgrade>}

      <div className="card">
        <State loading={loading && !data} error={error}>
          {data && (
            <>
              <p className="sub">{count(data.total)} record{data.total === 1 ? '' : 's'}{data.total > PAGE ? ` · showing ${offset + 1}–${Math.min(offset + PAGE, data.total)}` : ''}</p>
              {data.data.map((r) => <RecordRow key={r.id} r={r} />)}
              {!data.data.length && <div className="skeleton">Nothing matches these filters. <Link to="/records">Clear them</Link>.</div>}
              {data.total > PAGE && (
                <div className="pager">
                  <button className="btn small" disabled={offset === 0} onClick={() => setParams({ ...filters, offset: Math.max(0, offset - PAGE) })}>← Newer</button>
                  <button className="btn small" disabled={offset + PAGE >= data.total} onClick={() => setParams({ ...filters, offset: offset + PAGE })}>Older →</button>
                </div>
              )}
            </>
          )}
        </State>
      </div>
    </div>
  );
}
