// The weekly digest: a short public summary of the last seven days, used as
// the free newsletter and as ready-to-post text. Shows headlines only; the
// full record stays behind the plan's normal rules.
//   node server/digest.js            print this week's digest as Markdown
import { pathToFileURL } from 'node:url';
import { CATEGORIES, OUTCOMES, SITING } from './classify.js';
import { config } from './config.js';
import { addDays, openDb, today } from './db.js';
import { jurisdictionByClient } from './jurisdictions.js';

const PER_SECTION = 12;
const inSiting = `category IN (${SITING.map(() => '?').join(', ')})`;

const item = (r) => {
  const j = jurisdictionByClient.get(r.jurisdiction);
  const text = (r.project_name || r.title).replace(/\s+/g, ' ').trim();
  return {
    id: r.id,
    place: `${j?.name || r.jurisdiction}, ${r.state}`,
    date: r.event_date,
    agenda_date: r.agenda_date,
    category: r.category,
    outcome: r.outcome,
    restrictive: Boolean(r.restrictive),
    headline: text.length > 170 ? `${text.slice(0, 169)}…` : text,
    size: [r.acres && `${Math.round(r.acres).toLocaleString('en-US')} acres`, r.square_feet && `${Math.round(r.square_feet).toLocaleString('en-US')} sq ft`, r.mw && `${Math.round(r.mw)} MW`].filter(Boolean).join(', ') || null,
  };
};

/** Digest for the seven days ending on `end` (default: today). */
export function buildDigest(db, end = today()) {
  const start = addDays(end, -6);
  const week = db.prepare(`SELECT * FROM records WHERE ${inSiting} AND event_date BETWEEN ? AND ? ORDER BY event_date DESC, id DESC`).all(...SITING, start, end);
  const upcoming = db.prepare(`SELECT * FROM records WHERE ${inSiting} AND agenda_date > ? AND agenda_date <= ? ORDER BY agenda_date, id`).all(...SITING, end, addDays(end, 21));
  const yearAgo = db.prepare(`SELECT COUNT(*) AS n FROM records WHERE ${inSiting} AND restrictive = 1 AND event_date BETWEEN ? AND ?`).get(...SITING, addDays(end, -364), end).n;
  const priorYear = db.prepare(`SELECT COUNT(*) AS n FROM records WHERE ${inSiting} AND restrictive = 1 AND event_date BETWEEN ? AND ?`).get(...SITING, addDays(end, -729), addDays(end, -365)).n;
  const pick = (fn) => week.filter(fn).slice(0, PER_SECTION).map(item);
  const sections = [
    { key: 'restrictive', title: 'Moratoria, bans and limits', items: pick((r) => r.restrictive) },
    { key: 'projects', title: 'Project entitlements', items: pick((r) => r.category === 'project') },
    { key: 'policy', title: 'Other policy and regulation', items: pick((r) => r.category === 'policy' && !r.restrictive) },
    { key: 'money', title: 'Incentives, power and water', items: pick((r) => r.category === 'incentive' || r.category === 'utility') },
    { key: 'upcoming', title: 'Hearings in the next three weeks', items: upcoming.slice(0, PER_SECTION).map(item) },
  ].filter((s) => s.items.length);
  return {
    week: { start, end },
    counts: {
      records: week.length,
      places: new Set(week.map((r) => r.jurisdiction)).size,
      restrictive: week.filter((r) => r.restrictive).length,
      projects: week.filter((r) => r.category === 'project').length,
      upcoming: upcoming.length,
      restrictive_last_12_months: yearAgo,
      restrictive_prior_12_months: priorYear,
    },
    sections,
  };
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const day = (iso) => `${MONTHS[Number(iso.slice(5, 7)) - 1]} ${Number(iso.slice(8, 10))}`;

/** Plain Markdown, ready to paste into a newsletter or a post. */
export function digestMarkdown(d, baseUrl = config.publicUrl) {
  const c = d.counts;
  const out = [`# Data-centre siting: week of ${day(d.week.start)}–${day(d.week.end)}, ${d.week.end.slice(0, 4)}`, ''];
  out.push(c.records
    ? `${c.records} new or updated record${c.records === 1 ? '' : 's'} across ${c.places} local government${c.places === 1 ? '' : 's'} this week${c.restrictive ? `, including ${c.restrictive} that restrict development` : ''}.`
    : 'No new data-centre items in the covered local governments this week.');
  if (c.restrictive_last_12_months) out.push(`Restrictive actions in the last 12 months: ${c.restrictive_last_12_months} (${c.restrictive_prior_12_months} in the 12 months before).`);
  for (const s of d.sections) {
    out.push('', `## ${s.title}`, '');
    for (const i of s.items) {
      const when = s.key === 'upcoming' ? day(i.agenda_date) : day(i.date);
      const tag = s.key === 'upcoming' ? CATEGORIES[i.category] : OUTCOMES[i.outcome];
      out.push(`- **${i.place}** (${when}, ${tag.toLowerCase()}): ${i.headline}${i.size ? ` — ${i.size}` : ''} [source record](${baseUrl}/record/${i.id})`);
    }
  }
  out.push('', `Built from public meeting records by Siteline. Full records and alerts: ${baseUrl}`, '');
  return out.join('\n');
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
/** Store a digest sign-up. Returns 'added', 'exists' or 'invalid'. Sending needs an email provider and is not done here. */
export function subscribe(db, email) {
  email = String(email || '').trim().toLowerCase();
  if (!EMAIL_RE.test(email) || email.length > 254) return 'invalid';
  return db.prepare('INSERT OR IGNORE INTO subscribers (email, created_at) VALUES (?, ?)').run(email, new Date().toISOString()).changes ? 'added' : 'exists';
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const db = openDb(config.dbPath);
  console.log(digestMarkdown(buildDigest(db, process.argv[2] || today())));
  db.close();
}
