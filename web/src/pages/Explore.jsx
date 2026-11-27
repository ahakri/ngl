import { Link } from 'react-router-dom';
import { EcoToggle, SignalsTable, State, UpgradeNotice } from '../components/Bits.jsx';
import { useData, useEcosystem } from '../hooks.js';
import { fullDay, num, pct } from '../format.js';

export default function Explore() {
  const [eco, setEco] = useEcosystem();
  const meta = useData('/v1/meta');
  const up = useData(`/v1/movers?ecosystem=${eco}&limit=10`);
  const down = useData(`/v1/movers?ecosystem=${eco}&direction=down&limit=5`);
  const all = useData(`/v1/signals?ecosystem=${eco}`);

  const byCategory = new Map();
  for (const r of all.data?.data || []) {
    const c = byCategory.get(r.category) || { total: 0, leader: null, breakouts: 0 };
    c.total += r.downloads_28d;
    if (r.rank === 1) c.leader = r;
    if (r.breakout) c.breakouts += 1;
    byCategory.set(r.category, c);
  }
  const breakouts = (all.data?.data || []).filter((r) => r.breakout).sort((a, b) => b.momentum - a.momentum);
  const capped = up.data && up.data.limit_cap < 10;

  return (
    <div className="stack">
      <div className="row between">
        <div>
          <h1>Explore</h1>
          <p className="sub">Adoption signals across the AI developer stack{meta.data ? ` · data through ${fullDay(meta.data.as_of[eco])}` : ''}</p>
        </div>
        <EcoToggle value={eco} onChange={setEco} />
      </div>

      <div className="grid three">
        {(meta.data?.categories || []).filter((c) => c.ecosystems.includes(eco)).map((c) => {
          const s = byCategory.get(c.slug);
          return (
            <Link key={c.slug} to={`/category/${c.slug}`} className="card" style={{ color: 'inherit', textDecoration: 'none' }}>
              <h3>{c.name}</h3>
              <div className="tile" style={{ marginTop: 6 }}>
                <div className="value" style={{ fontSize: 22 }}>{s ? num(s.total) : '—'}</div>
                <div className="note">downloads, 28 days{s?.breakouts ? ` · ${s.breakouts} breakout${s.breakouts > 1 ? 's' : ''}` : ''}</div>
              </div>
              {s?.leader && <p className="sub" style={{ marginTop: 8 }}>Leader: {s.leader.name} ({pct(s.leader.share, 0)})</p>}
            </Link>
          );
        })}
      </div>

      <div className="grid two">
        <div className="card">
          <h2>Gaining momentum</h2>
          <p className="sub">Highest momentum scores, minimum 10K downloads in 28 days.</p>
          <State loading={up.loading} error={up.error}>{up.data && <SignalsTable rows={up.data.data} showShare={false} />}</State>
          {capped && <div style={{ marginTop: 12 }}><UpgradeNotice>Free shows the top {up.data.limit_cap}. Pro unlocks the full ranking.</UpgradeNotice></div>}
        </div>
        <div className="card">
          <h2>Losing momentum</h2>
          <p className="sub">Lowest momentum scores over the same window.</p>
          <State loading={down.loading} error={down.error}>{down.data && <SignalsTable rows={down.data.data} showShare={false} />}</State>
        </div>
      </div>

      <div className="card">
        <h2>Breakouts</h2>
        <p className="sub">Growing at least 20% over 28 days, still accelerating, and taking share from their category.</p>
        <State loading={all.loading} error={all.error}>
          {breakouts.length ? <SignalsTable rows={breakouts} /> : <div className="skeleton">No breakouts on {eco} right now.</div>}
        </State>
      </div>
    </div>
  );
}
