import { useCallback, useEffect, useState } from 'react';
import { Link, NavLink, Route, Routes, useLocation } from 'react-router-dom';
import { api } from './api.js';
import { SessionContext } from './hooks.js';
import Home from './pages/Home.jsx';
import Explore from './pages/Explore.jsx';
import Category from './pages/Category.jsx';
import Project from './pages/Project.jsx';
import Models from './pages/Models.jsx';
import Pricing from './pages/Pricing.jsx';
import Docs from './pages/Docs.jsx';
import Account from './pages/Account.jsx';
import { Privacy, Terms } from './pages/Legal.jsx';

function ScrollTop() {
  const { pathname } = useLocation();
  useEffect(() => window.scrollTo(0, 0), [pathname]);
  return null;
}

export default function App() {
  const [session, setSession] = useState({ user: null, me: null, ready: false });
  const [config, setConfig] = useState(null);
  const refresh = useCallback(
    () => api.get('/api/me').then((me) => setSession({ user: me.user, me, ready: true }), () => setSession({ user: null, me: null, ready: true })),
    [],
  );
  useEffect(() => {
    refresh();
    api.get('/api/config').then(setConfig, () => {});
  }, [refresh]);

  const link = ({ isActive }) => `link${isActive ? ' active' : ''}`;
  return (
    <SessionContext.Provider value={{ ...session, config, refresh }}>
      <ScrollTop />
      <header className="nav">
        <div className="wrap">
          <Link to="/" className="brand">
            <svg width="22" height="22" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="7" fill="var(--text-primary)" /><path d="M7 22l6-7 4 4 8-10" fill="none" stroke="var(--surface-1)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" /></svg>
            Uptake
          </Link>
          <NavLink to="/explore" className={link}>Explore</NavLink>
          <NavLink to="/models" className={link}>Open models</NavLink>
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
            <Route path="/explore" element={<Explore />} />
            <Route path="/category/:slug" element={<Category />} />
            <Route path="/project/:slug" element={<Project />} />
            <Route path="/models" element={<Models />} />
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
          <span>Uptake · AI ecosystem adoption data · <Link to="/terms">Terms</Link> · <Link to="/privacy">Privacy</Link></span>
          <span>Sources: PyPI download logs, npm registry, Hugging Face Hub, Hacker News. Aggregate public data only — no personal data.</span>
        </div>
      </footer>
    </SessionContext.Provider>
  );
}
