export const usd = (v) => {
  if (v === null || v === undefined) return '—';
  const a = Math.abs(v);
  if (a >= 1e6) return `$${(v / 1e6).toFixed(a >= 1e7 ? 1 : 2)}M`;
  if (a >= 1e4) return `$${Math.round(v / 1e3)}K`;
  if (a >= 1e3) return `$${(v / 1e3).toFixed(1)}K`;
  return `$${Math.round(v)}`;
};
export const usdFull = (v) => (v === null || v === undefined ? '—' : `$${Math.round(v).toLocaleString('en-US')}`);
export const count = (v) => (v === null || v === undefined ? '—' : Math.round(v).toLocaleString('en-US'));
export const pct = (v, digits = 0) => (v === null || v === undefined ? '—' : `${(v * 100).toFixed(digits)}%`);
export const ordinal = (p) => {
  const n = Math.round(p * 100);
  const s = n % 100 >= 11 && n % 100 <= 13 ? 'th' : ['th', 'st', 'nd', 'rd'][n % 10] || 'th';
  return `${n}${s}`;
};
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
export const fullDay = (iso) => (iso ? `${MONTHS[Number(iso.slice(5, 7)) - 1]} ${Number(iso.slice(8, 10))}, ${iso.slice(0, 4)}` : '—');
export const quarter = (q) => (q ? `${q.slice(5)} ${q.slice(0, 4)}` : '—');
