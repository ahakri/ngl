import { Link } from 'react-router-dom';
import { State } from '../components/Bits.jsx';
import { useData, useSession } from '../hooks.js';
import { count, usd, usdFull } from '../format.js';
import { PlanCards } from './Pricing.jsx';

/** Ranked medians with the value written on each bar. */
function MedianBars({ rows }) {
  const max = Math.max(...rows.map((r) => r.median), 1);
  return (
    <div style={{ display: 'grid', gap: 7 }}>
      {rows.map((r) => (
        <div key={r.key} title={`${r.label}: median ${usdFull(r.median)} across ${count(r.n)} deals`} style={{ display: 'grid', gridTemplateColumns: 'minmax(110px, 32%) 1fr 62px', gap: 10, alignItems: 'center', fontSize: 13.5 }}>
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.label}</span>
          <span style={{ height: 14 }}><i style={{ display: 'block', height: '100%', width: `${Math.max(1, (r.median / max) * 100)}%`, background: 'var(--series-1)', borderRadius: '0 4px 4px 0' }} /></span>
          <span style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{usd(r.median)}</span>
        </div>
      ))}
    </div>
  );
}

export default function Home() {
  const { user } = useSession();
  const { data, loading, error } = useData('/v1/summary');
  const ds = data?.dataset;
  const empty = ds && ds.deals === 0;

  return (
    <div>
      <section className="hero">
        <div className="eyebrow">NIL deal benchmarks</div>
        <h1>Know what an NIL deal is really worth — from the athletes who signed them.</h1>
        <p className="lead">
          Every NIL deal now has to hold up as fair value, but nobody publishes what comparable deals pay.
          Rangefinder is an anonymous database of real deals, shared by athletes. Share one of yours and see them all.
        </p>
        <div className="row">
          <Link to={user ? '/submit' : '/account?next=submit'} className="btn primary">Share a deal, unlock the data</Link>
          <Link to="/pricing" className="btn">For agents, brands and schools</Link>
        </div>
      </section>

      <State loading={loading} error={error}>
        {data && (
          <>
            <div className="grid four" style={{ marginTop: 18 }}>
              <div className="card tile"><div className="label">Deals in the database</div><div className="value">{count(ds.deals)}</div><div className="note">{ds.verified ? `${count(ds.verified)} verified by a moderator` : 'self-reported and screened'}</div></div>
              <div className="card tile"><div className="label">Total deal value</div><div className="value">{usd(ds.total_value_usd)}</div><div className="note">cash and in-kind</div></div>
              <div className="card tile"><div className="label">Median deal</div><div className="value">{data.overall.suppressed ? '—' : usdFull(data.overall.median)}</div><div className="note">across all sports</div></div>
              <div className="card tile"><div className="label">Sports covered</div><div className="value">{ds.sports}</div><div className="note">all NCAA divisions, NAIA and JUCO</div></div>
            </div>

            {empty ? (
              <section className="section">
                <div className="card">
                  <h2>Be one of the first</h2>
                  <p className="sub" style={{ marginTop: 6 }}>The database is just opening. Benchmarks appear for a group as soon as five athletes in it have shared a deal — nothing is published below that, to keep every contributor anonymous.</p>
                </div>
              </section>
            ) : (
              <section className="section">
                <h2>What deals pay, at a glance</h2>
                <p className="sub">Median total value per deal. Members also see the full range, by competition level, follower count, payer and more.</p>
                <div className="grid two">
                  <div className="card"><h3 style={{ marginBottom: 12 }}>By sport</h3><MedianBars rows={data.by_sport.slice(0, 10)} /></div>
                  <div className="card"><h3 style={{ marginBottom: 12 }}>By deal type</h3><MedianBars rows={data.by_deal_type} /></div>
                </div>
              </section>
            )}
          </>
        )}
      </State>

      <section className="section">
        <h2>How it works</h2>
        <div className="grid three steps" style={{ marginTop: 14 }}>
          <div className="card"><h3>Share a deal anonymously</h3><p className="sub">Two minutes. Sport, level, follower range, what you did and what it paid. Never your name, school or the brand.</p></div>
          <div className="card"><h3>Unlock every benchmark</h3><p className="sub">See what comparable athletes were paid for comparable work, free for a year for each deal you share.</p></div>
          <div className="card"><h3>Price your next deal</h3><p className="sub">The range finder shows where an offer sits against real deals, and what the typical range is before you sign.</p></div>
        </div>
      </section>

      <section className="section">
        <h2>Why this data did not exist</h2>
        <div className="grid three" style={{ marginTop: 14 }}>
          <div className="card"><h3>Deals are private</h3><p className="sub">Terms sit in individual contracts. Public "valuations" are estimates, not what anyone was actually paid.</p></div>
          <div className="card"><h3>The stakes went up</h3><p className="sub">Third-party deals of $600 or more are now reviewed against a range of compensation for similar athletes. A deal priced outside it can be refused.</p></div>
          <div className="card"><h3>Only athletes hold the answers</h3><p className="sub">So the database is built by them, and built so that no single athlete can be picked out: every figure covers at least five deals.</p></div>
        </div>
      </section>

      <section className="section">
        <h2>Access</h2>
        <p className="sub">Free for athletes who contribute. Subscriptions for everyone who needs the data professionally.</p>
        <PlanCards />
      </section>
    </div>
  );
}
