import { Link, useParams } from 'react-router-dom';
import LineChart from '../components/LineChart.jsx';
import { EcoToggle, SignalsTable, State, UpgradeNotice } from '../components/Bits.jsx';
import { useData, useEcosystem } from '../hooks.js';
import { fullDay, num, pct } from '../format.js';
import { topShare } from './Home.jsx';

export default function Category() {
  const { slug } = useParams();
  const [eco, setEco] = useEcosystem();
  const meta = useData('/v1/meta');
  const info = meta.data?.categories.find((c) => c.slug === slug);
  const ecosystems = info?.ecosystems || ['pypi', 'npm'];
  const active = ecosystems.includes(eco) ? eco : ecosystems[0];
  const { data, loading, error } = useData(`/v1/categories/${slug}?ecosystem=${active}`);

  return (
    <div className="stack">
      <div className="row between">
        <div>
          <p className="sub"><Link to="/explore">Explore</Link> / Category</p>
          <h1>{data?.category.name || info?.name || 'Category'}</h1>
          <p className="sub" style={{ maxWidth: 640 }}>{data?.category.blurb}</p>
        </div>
        <EcoToggle value={active} onChange={setEco} options={ecosystems} />
      </div>
      <State loading={loading} error={error}>
        {data && (
          <>
            <div className="card">
              <div className="row between">
                <div>
                  <h2>Market share</h2>
                  <p className="sub">Share of trailing-28-day downloads, sampled weekly · {num(data.total_downloads_28d)} downloads in the latest window · through {fullDay(data.as_of)}</p>
                </div>
              </div>
              <LineChart dates={data.share.dates} series={topShare(data.share, 7)} format={(v) => pct(v, 0)} ariaLabel={`${data.category.name} market share`} />
              {data.regime_start && <p className="sub" style={{ marginTop: 8 }}>History starts after the registry's counting change on {fullDay(data.regime_start)}; earlier figures are not comparable.</p>}
              {data.plan === 'free' && <div style={{ marginTop: 12 }}><UpgradeNotice>Free shows the last 12 weeks. Pro and Team include full history and CSV export.</UpgradeNotice></div>}
            </div>
            <div className="card">
              <h2>Leaderboard</h2>
              <p className="sub">Ranked by downloads over the last 28 days. Arrows show rank changes versus 28 days earlier.</p>
              <SignalsTable rows={data.leaderboard} showRank />
            </div>
          </>
        )}
      </State>
    </div>
  );
}
