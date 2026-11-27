import { Link, useParams } from 'react-router-dom';
import LineChart from '../components/LineChart.jsx';
import { Delta, Momentum, State, UpgradeNotice } from '../components/Bits.jsx';
import { useData } from '../hooks.js';
import { ECO_LABEL, SERIES, day, num, pct, points } from '../format.js';

/** Trailing 7-day mean — removes the weekday sawtooth from daily downloads. */
function rolling7(points) {
  return points.map((_, i) => (i < 6 ? null : points.slice(i - 6, i + 1).reduce((s, p) => s + p.downloads, 0) / 7));
}

function Stat({ label, children, note }) {
  return <div className="tile"><div className="label">{label}</div><div className="value" style={{ fontSize: 21 }}>{children}</div>{note && <div className="note">{note}</div>}</div>;
}

export default function Project() {
  const { slug } = useParams();
  const { data, loading, error } = useData(`/v1/projects/${slug}`);

  return (
    <State loading={loading} error={error}>
      {data && (
        <div className="stack">
          <div>
            <p className="sub"><Link to="/explore">Explore</Link> / <Link to={`/category/${data.project.category}`}>{data.project.category_name}</Link></p>
            <h1>{data.project.name}</h1>
            <p className="sub">{data.project.vendor}</p>
          </div>
          {data.signals.map((s) => {
            const pts = data.series[s.ecosystem] || [];
            const breaks = data.quality.structural_breaks.filter((b) => b.ecosystem === s.ecosystem).map((b) => ({ date: b.date, label: 'counting change' }));
            return (
              <div className="card" key={s.ecosystem}>
                <div className="row between">
                  <div>
                    <h2>{ECO_LABEL[s.ecosystem]} {s.breakout && <span className="badge hot">Breakout</span>}</h2>
                    <p className="sub mono">{s.package}</p>
                  </div>
                  <span className="sub">#{s.rank} in {data.project.category_name}</span>
                </div>
                <div className="grid four" style={{ margin: '14px 0 6px' }}>
                  <Stat label="Downloads, 28 days" note={`${num(s.downloads_7d)} in the last 7`}>{num(s.downloads_28d)}</Stat>
                  <Stat label="Growth, 28 days" note={<>7 days: <Delta v={s.growth_7d} /></>}><Delta v={s.growth_28d} /></Stat>
                  <Stat label="Category share" note={<>vs 28 days ago: <Delta v={s.share_delta_28d} fmt={points} /></>}>{pct(s.share)}</Stat>
                  <Stat label="Momentum" note="0–100, 50 is flat"><Momentum v={s.momentum} /></Stat>
                </div>
                <h3 style={{ marginTop: 10 }}>Daily downloads</h3>
                <p className="sub">7-day average</p>
                <LineChart dates={pts.map((p) => p.date)} series={[{ name: 'Daily downloads (7-day avg)', color: SERIES[0], values: rolling7(pts) }]} format={num} height={240} markers={breaks} ariaLabel={`${data.project.name} ${s.ecosystem} downloads`} />
              </div>
            );
          })}
          {!data.signals.length && <div className="card"><div className="skeleton">No download data collected for this project yet.</div></div>}
          {data.attention && (
            <div className="card">
              <h2>Developer attention</h2>
              <p className="sub">Hacker News stories mentioning “{data.project.hn_query}”, per week. A leading indicator, not a usage measure.</p>
              <LineChart dates={data.attention.weekly.map((w) => w.week_ending)} series={[{ name: 'Stories per week', color: SERIES[1], values: data.attention.weekly.map((w) => w.value) }]} format={(v) => (Number.isInteger(v) ? String(v) : v.toFixed(1))} height={200} ariaLabel="Hacker News stories per week" />
            </div>
          )}
          {data.plan === 'free' && <UpgradeNotice>Showing {data.history_days} days{data.series.pypi?.length || data.series.npm?.length ? ` (from ${day((data.series.pypi || data.series.npm)[0].date)})` : ''}. Pro and Team include full history and CSV export.</UpgradeNotice>}
        </div>
      )}
    </State>
  );
}
