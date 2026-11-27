import { useCallback, useEffect, useState } from 'react';
import { Link, NavLink, Route, Routes, useLocation } from 'react-router-dom';
import { api } from './api.js';
import { SessionContext } from './hooks.js';
import Home from './pages/Home.jsx';
import Benchmarks from './pages/Benchmarks.jsx';
import RangeFinder from './pages/RangeFinder.jsx';
import Submit from './pages/Submit.jsx';
import Pricing from './pages/Pricing.jsx';
import Docs from './pages/Docs.jsx';
import Account from './pages/Account.jsx';
import Admin from './pages/Admin.jsx';
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
  // Access changes when you sign in or share a deal, so meta reloads with the session.
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
      {meta?.dataset.demo_data && (
        <div className="banner"><div className="wrap"><b>Sample data.</b> The figures on this site are generated for demonstration and are not real deals.</div></div>
      )}
      <header className="nav">
        <div className="wrap">
          <Link to="/" className="brand">
            <svg width="22" height="22" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="7" fill="var(--text-primary)" /><path d="M6 16h20M11 11v10M21 11v10" fill="none" stroke="var(--surface-1)" strokeWidth="3" strokeLinecap="round" /></svg>
            Rangefinder
          </Link>
          <NavLink to="/benchmarks" className={link}>Benchmarks</NavLink>
          <NavLink to="/range-finder" className={link}>Range finder</NavLink>
          <NavLink to="/submit" className={link}>Share a deal</NavLink>
          <NavLink to="/pricing" className={link}>Pricing</NavLink>
          <NavLink to="/docs" className={link}>API</NavLink>
          <span className="spacer" />
          {session.me?.is_admin && <NavLink to="/admin" className={link}>Review</NavLink>}
          {session.ready && (session.user
            ? <NavLink to="/account" className={link}>Account</NavLink>
            : <Link to="/account" className="btn small primary">Sign in</Link>)}
        </div>
      </header>
      <main>
        <div className="wrap">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/benchmarks" element={<Benchmarks />} />
            <Route path="/range-finder" element={<RangeFinder />} />
            <Route path="/submit" element={<Submit />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/docs" element={<Docs />} />
            <Route path="/account" element={<Account />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/terms" element={<Terms />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="*" element={<div className="card"><h2>Page not found</h2><p className="sub"><Link to="/">Back to the start</Link></p></div>} />
          </Routes>
        </div>
      </main>
      <footer>
        <div className="wrap">
          <span>Rangefinder · NIL deal benchmarks · <Link to="/terms">Terms</Link> · <Link to="/privacy">Privacy</Link></span>
          <span>Anonymous by design: no names, schools or brands are collected. Not affiliated with the NCAA, the College Sports Commission or NIL Go.</span>
        </div>
      </footer>
    </SessionContext.Provider>
  );
}
