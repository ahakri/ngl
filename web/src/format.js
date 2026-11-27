export const num = (v) => {
  if (v === null || v === undefined) return '—';
  const a = Math.abs(v);
  if (a >= 1e9) return `${(v / 1e9).toFixed(a >= 1e10 ? 1 : 2)}B`;
  if (a >= 1e6) return `${(v / 1e6).toFixed(a >= 1e8 ? 0 : 1)}M`;
  if (a >= 1e3) return `${(v / 1e3).toFixed(a >= 1e5 ? 0 : 1)}K`;
  return String(Math.round(v));
};
export const pct = (v, digits = 1) => (v === null || v === undefined ? '—' : `${(v * 100).toFixed(digits)}%`);
export const signedPct = (v, digits = 1) => (v === null || v === undefined ? '—' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v * 100).toFixed(digits)}%`);
export const points = (v) => (v === null || v === undefined ? '—' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v * 100).toFixed(1)} pp`);
export const tone = (v) => (v === null || v === undefined || Math.abs(v) < 0.0005 ? 'muted' : v > 0 ? 'up' : 'down');
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
export const day = (iso) => (iso ? `${MONTHS[Number(iso.slice(5, 7)) - 1]} ${Number(iso.slice(8, 10))}` : '—');
export const fullDay = (iso) => (iso ? `${day(iso)}, ${iso.slice(0, 4)}` : '—');
export const ECO_LABEL = { pypi: 'PyPI (Python)', npm: 'npm (JS/TS)' };
export const SERIES = [1, 2, 3, 4, 5, 6, 7, 8].map((i) => `var(--series-${i})`);
