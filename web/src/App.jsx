import { useCallback, useEffect, useState } from 'react';
import { Link, NavLink, Route, Routes, useLocation } from 'react-router-dom';
import { api } from './api.js';
import { SessionContext } from './hooks.js';
import Home from './pages/Home.jsx';
import Records from './pages/Records.jsx';
import RecordDetail from './pages/RecordDetail.jsx';
import Calendar from './pages/Calendar.jsx';
import Pricing from './pages/Pricing.jsx';
import Docs from './pages/Docs.jsx';
import Account from './pages/Account.jsx';
import Coverage from './pages/Coverage.jsx';
import { Privacy, Terms } from './pages/Legal.jsx';

function ScrollTop() {
  const { pathname } = useLocation();
  // Braces matter: newer browsers return a Promise from scrollTo, which React would treat as a cleanup.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

export default function App() {
  const [session, setSession] = useState({ user: null, me: null, ready: false });
  const [meta, setMeta] = useState(null);
  const [config, setConfig] = useState(null);
  // Access depends on the signed-in plan, so meta reloads with the session.
  const refresh = useCallback(async () => {
    await api.get('/api/me').then((me) => setSession({ user: me.user, me, ready: true }), () => setSession({ user: null, me: null, ready: true }));
    await api.get('/v1/meta').then(setMeta, () => {});
  }, []);
  useEffect(() => {
    refresh();
    api.get('/api/config').then(setConfig, () => {});
  }, [refresh]);

  const link = ({ isActive }) => `link${isActive ? ' active' : ''}`;
  return (
    <SessionContext.Provider value={{ ...session, meta, config, refresh }}>
      <ScrollTop />
      <header className="nav">
        <div className="wrap">
          <Link to="/" className="brand">
            <svg width="22" height="22" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="7" fill="var(--text-primary)" /><path d="M16 7c-3.9 0-7 3-7 6.8C9 19 16 25 16 25s7-6 7-11.2C23 10 19.9 7 16 7z" fill="none" stroke="var(--surface-1)" strokeWidth="2.6" /><circle cx="16" cy="14" r="2.4" fill="var(--surface-1)" /></svg>
            Siteline
          </Link>
          <NavLink to="/records" className={link}>Records</NavLink>
          <NavLink to="/calendar" className={link}>Calendar</NavLink>
          <NavLink to="/coverage" className={link}>Coverage</NavLink>
          <NavLink to="/pricing" className={link}>Pricing</NavLink>
          <NavLink to="/docs" className={link}>API</NavLink>
          <span className="spacer" />
          {session.ready && (session.user
            ? <NavLink to="/account" className={link}>Account</NavLink>
            : <Link to="/account" className="btn small primary">Sign in</Link>)}
        </div>
      </header>
      <main>
        <div className="wrap">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/records" element={<Records />} />
            <Route path="/record/:id" element={<RecordDetail />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/coverage" element={<Coverage />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/docs" element={<Docs />} />
            <Route path="/account" element={<Account />} />
            <Route path="/terms" element={<Terms />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="*" element={<div className="card"><h2>Page not found</h2><p className="sub"><Link to="/">Back to the start</Link></p></div>} />
          </Routes>
        </div>
      </main>
      <footer>
        <div className="wrap">
          <span>Siteline · data-centre siting records · <Link to="/terms">Terms</Link> · <Link to="/privacy">Privacy</Link></span>
          <span>Built from public meeting and legislative records. Every record links to its official source.</span>
        </div>
      </footer>
    </SessionContext.Provider>
  );
}
