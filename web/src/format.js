export const count = (v) => (v === null || v === undefined ? '—' : Math.round(v).toLocaleString('en-US'));
export const compact = (v) => {
  if (v === null || v === undefined) return '—';
  if (v >= 1e6) return `${(v / 1e6).toFixed(v >= 1e7 ? 0 : 1)}M`;
  if (v >= 1e4) return `${Math.round(v / 1e3)}K`;
  return Math.round(v).toLocaleString('en-US');
};
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
export const fullDay = (iso) => (iso ? `${MONTHS[Number(iso.slice(5, 7)) - 1]} ${Number(iso.slice(8, 10))}, ${iso.slice(0, 4)}` : '—');
export const quarter = (q) => `${q.slice(5)} ’${q.slice(2, 4)}`;
export const change = (now, before) => (before > 0 ? `${now >= before ? '+' : '−'}${Math.abs(Math.round((now / before - 1) * 100))}% vs prior 12 months` : before === 0 && now > 0 ? 'none in the prior 12 months' : '');
export const size = (r) => [r.acres && `${count(r.acres)} acres`, r.square_feet && `${compact(r.square_feet)} sq ft`, r.mw && `${count(r.mw)} MW`].filter(Boolean).join(' · ');
export const CATEGORY_COLOR = { project: 'var(--series-1)', policy: 'var(--series-2)', incentive: 'var(--series-3)', utility: 'var(--series-4)' };
