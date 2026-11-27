import { createContext, useContext, useEffect, useState } from 'react';
import { api } from './api.js';

/** Fetch JSON for a path; refetches when the path changes. */
export function useData(path) {
  const [state, setState] = useState({ data: null, error: null, loading: Boolean(path) });
  useEffect(() => {
    if (!path) return undefined;
    let live = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    api.get(path).then(
      (data) => live && setState({ data, error: null, loading: false }),
      (error) => live && setState({ data: null, error, loading: false }),
    );
    return () => {
      live = false;
    };
  }, [path]);
  return state;
}

export const SessionContext = createContext({ user: null, me: null, meta: null, config: null, refresh: () => {} });
export const useSession = () => useContext(SessionContext);
