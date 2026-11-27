import { Link } from 'react-router-dom';
import QuarterChart from '../components/QuarterChart.jsx';
import { RecordRow, State } from '../components/Bits.jsx';
import { useData, useSession } from '../hooks.js';
import { change, count, fullDay } from '../format.js';
import { PlanCards } from './Pricing.jsx';

export default function Home() {
  const { meta } = useSession();
  const { data, loading, error } = useData('/v1/summary');
  const recent = useData('/v1/records?limit=5');
  const t = data?.totals;

  return (
    <div>
      <section className="hero">
        <div className="eyebrow">Data-centre siting intelligence</div>
        <h1>Every data-centre hearing, moratorium and rezoning — in one feed.</h1>
        <p className="lead">
          Whether a data centre gets built is now decided in city halls and county boardrooms. Siteline reads the public record of
          those meetings every day and turns it into structured, searchable siting data: projects, policy changes, incentives and power deals.
        </p>
        <div className="row">
          <Link to="/records" className="btn primary">Browse the records</Link>
          <Link to="/digest" className="btn">This week's digest</Link>
        </div>
      </section>

      <State loading={loading} error={error}>
        {data && (
          <>
            <div className="grid four" style={{ marginTop: 18 }}>
              <div className="card tile"><div className="label">Siting records, last 12 months</div><div className="value">{count(t.last_12_months)}</div><div className="note">{change(t.last_12_months, t.prior_12_months)}</div></div>
              <div className="card tile"><div className="label">Restrictive actions, last 12 months</div><div className="value">{count(t.restrictive_last_12_months)}</div><div className="note">moratoria, bans and limits · {t.restrictive_prior_12_months} the year before</div></div>
              <div className="card tile"><div className="label">Hearings scheduled</div><div className="value">{count(t.upcoming_hearings)}</div><div className="note">on a published future agenda</div></div>
              <div className="card tile"><div className="label">Jurisdictions covered</div><div className="value">{data.coverage.jurisdictions}</div><div className="note">in {data.coverage.states} states · synced {fullDay(data.coverage.last_sync)}</div></div>
            </div>

            <section className="section">
              <h2>Local action on data centres has surged since 2025</h2>
              <p className="sub">Siting records per quarter across covered jurisdictions, by type. The latest quarter is still in progress. Hover a column for the count that restricts development.</p>
              <div className="card">{meta && <QuarterChart rows={data.by_quarter.slice(-12)} labels={meta.categories} />}</div>
            </section>

            <section className="section">
              <h2>Where the activity is</h2>
              <p className="sub">Last 12 months, covered jurisdictions only.</p>
              <div className="card">
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>State</th><th className="num">Records</th><th className="num">Project entitlements</th><th className="num">Restrictive actions</th></tr></thead>
                    <tbody>{data.by_state.slice(0, 10).map((s) => <tr key={s.state}><td className="name"><Link to={`/records?state=${s.state}`}>{s.state}</Link></td><td className="num">{s.records}</td><td className="num">{s.projects}</td><td className="num">{s.restrictive}</td></tr>)}</tbody>
                  </table>
                </div>
              </div>
            </section>
          </>
        )}
      </State>

      <section className="section">
        <h2>From the record</h2>
        <p className="sub">Real items from official agendas. The free view runs 30 days behind; subscribers see them the day they are published.</p>
        <div className="card"><State loading={recent.loading} error={recent.error}>{recent.data?.data.map((r) => <RecordRow key={r.id} r={r} />)}</State></div>
      </section>

      <section className="section">
        <h2>Who uses it</h2>
        <div className="grid three" style={{ marginTop: 14 }}>
          <div className="card"><h3>Developers and site selectors</h3><p className="sub">See which jurisdictions are approving, stalling or freezing projects before committing to land, and track competitors' entitlements case by case.</p></div>
          <div className="card"><h3>Land brokers and suppliers</h3><p className="sub">Find projects when they first reach a planning agenda — with acreage, square footage and case numbers — months before they are announced.</p></div>
          <div className="card"><h3>Investors, utilities and counsel</h3><p className="sub">Measure local permitting risk with evidence: moratoria, incentive reversals, large-load rate cases and the vote on each.</p></div>
        </div>
      </section>

      <section className="section">
        <h2>Plans</h2>
        <p className="sub">Free runs 30 days behind. Paid plans are live, with alerts, export and API.</p>
        <PlanCards />
      </section>
    </div>
  );
}
