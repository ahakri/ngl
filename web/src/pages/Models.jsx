import { useState } from 'react';
import { BarList, Delta, State, UpgradeNotice } from '../components/Bits.jsx';
import { useData } from '../hooks.js';
import { fullDay, num, pct } from '../format.js';

export default function Models() {
  const [sort, setSort] = useState('trending');
  const orgs = useData('/v1/models/orgs?limit=12');
  const tasks = useData('/v1/models/tasks?limit=12');
  const models = useData(`/v1/models?sort=${sort}&limit=25`);
  const bars = (d, key) => d.rows.map((r) => ({ label: r[key], value: r.share, display: pct(r.share) }));

  return (
    <div className="stack">
      <div>
        <h1>Open models</h1>
        <p className="sub" style={{ maxWidth: 700 }}>
          Who ships the open weights developers actually pull. Built from a daily snapshot of the most-downloaded and trending models on the Hugging Face Hub
          {orgs.data?.as_of ? ` · snapshot ${fullDay(orgs.data.as_of)} · ${num(orgs.data.total_downloads_30d)} downloads in 30 days across the panel` : ''}.
        </p>
      </div>
      <div className="grid two">
        <div className="card">
          <h2>Share by organisation</h2>
          <p className="sub">Share of trailing-30-day downloads within the panel.</p>
          <div style={{ marginTop: 12 }}><State loading={orgs.loading} error={orgs.error}>{orgs.data && <BarList rows={bars(orgs.data, 'org')} />}</State></div>
        </div>
        <div className="card">
          <h2>Share by task</h2>
          <p className="sub">What the downloaded models are for.</p>
          <div style={{ marginTop: 12 }}><State loading={tasks.loading} error={tasks.error}>{tasks.data && <BarList rows={bars(tasks.data, 'task')} />}</State></div>
        </div>
      </div>
      <div className="card">
        <div className="row between">
          <div>
            <h2>Models</h2>
            <p className="sub">{models.data?.compared_to ? `Change is versus the ${fullDay(models.data.compared_to)} snapshot.` : 'Week-over-week change appears once a second snapshot has been collected.'}</p>
          </div>
          <div className="seg" role="group" aria-label="Sort">
            {[['trending', 'Trending'], ['downloads', 'Most downloaded'], ['likes', 'Most liked']].map(([k, label]) => (
              <button key={k} className={sort === k ? 'on' : ''} onClick={() => setSort(k)} aria-pressed={sort === k}>{label}</button>
            ))}
          </div>
        </div>
        <State loading={models.loading} error={models.error}>
          {models.data && (
            <div className="table-wrap">
              <table>
                <thead><tr><th className="num">#</th><th>Model</th><th>Task</th><th className="num">Downloads, 30d</th><th className="num">Change</th><th className="num">Likes</th><th className="num hide-sm">Trending</th></tr></thead>
                <tbody>
                  {models.data.rows.map((r) => (
                    <tr key={r.id}>
                      <td className="num">{r.rank}</td>
                      <td className="name"><a href={`https://huggingface.co/${r.id}`} target="_blank" rel="noreferrer">{r.id.split('/').pop()}</a><div className="vendor">{r.org}</div></td>
                      <td>{r.task || <span className="muted">—</span>}</td>
                      <td className="num">{num(r.downloads_30d)}</td>
                      <td className="num"><Delta v={r.downloads_change} /></td>
                      <td className="num">{num(r.likes)}</td>
                      <td className="num hide-sm">{r.trending_score == null ? '—' : Math.round(r.trending_score)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </State>
        {models.data?.limit_cap <= 25 && <div style={{ marginTop: 12 }}><UpgradeNotice>Free shows the top 25. Pro covers the top 500; Team the full panel.</UpgradeNotice></div>}
      </div>
    </div>
  );
}
