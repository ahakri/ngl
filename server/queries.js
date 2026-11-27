// Read side: filtered record lists, detail, summary statistics and feeds.
import crypto from 'node:crypto';
import { CATEGORIES, OUTCOMES, SITING } from './classify.js';
import { addDays, today } from './db.js';
import { JURISDICTIONS, jurisdictionByClient } from './jurisdictions.js';

const STATES = [...new Set(JURISDICTIONS.map((j) => j.state))].sort();

const present = (r) => {
  const j = jurisdictionByClient.get(r.jurisdiction);
  return {
    id: r.id,
    jurisdiction: { code: r.jurisdiction, name: j?.name || r.jurisdiction, state: r.state, kind: j?.kind || null },
    category: r.category,
    restrictive: Boolean(r.restrictive),
    outcome: r.outcome,
    event_date: r.event_date,
    title: r.title,
    file: r.file,
    project_name: r.project_name,
    case_number: r.case_number,
    acres: r.acres,
    square_feet: r.square_feet,
    mw: r.mw,
    staff_recommendation: r.staff_recommendation,
    body: r.body_name,
    item_type: r.type_name,
    local_status: r.status_name,
    introduced: r.intro_date,
    agenda_date: r.agenda_date,
    source_url: r.url,
  };
};

export class FilterError extends Error {}

/** Validate filters from a query string or stored watch. */
export function parseFilters(src = {}) {
  const f = {};
  if (src.state) {
    if (!STATES.includes(String(src.state).toUpperCase())) throw new FilterError(`Unknown or uncovered state: ${src.state}`);
    f.state = String(src.state).toUpperCase();
  }
  if (src.jurisdiction) {
    if (!jurisdictionByClient.has(src.jurisdiction)) throw new FilterError(`Unknown jurisdiction: ${src.jurisdiction}`);
    f.jurisdiction = src.jurisdiction;
  }
  if (src.category) {
    if (!SITING.includes(src.category)) throw new FilterError(`category must be one of: ${SITING.join(', ')}`);
    f.category = src.category;
  }
  if (src.outcome) {
    if (!Object.hasOwn(OUTCOMES, src.outcome)) throw new FilterError(`outcome must be one of: ${Object.keys(OUTCOMES).join(', ')}`);
    f.outcome = src.outcome;
  }
  if (src.restrictive === '1' || src.restrictive === 'true' || src.restrictive === true) f.restrictive = true;
  for (const k of ['since', 'until']) {
    if (src[k]) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(src[k])) throw new FilterError(`${k} must be YYYY-MM-DD`);
      f[k] = src[k];
    }
  }
  if (src.q) f.q = String(src.q).slice(0, 80);
  return f;
}

function where(f, embargoDays) {
  const sql = [`category IN (${SITING.map(() => '?').join(', ')})`];
  const args = [...SITING];
  const add = (clause, ...v) => { sql.push(clause); args.push(...v); };
  if (f.state) add('state = ?', f.state);
  if (f.jurisdiction) add('jurisdiction = ?', f.jurisdiction);
  if (f.category) add('category = ?', f.category);
  if (f.outcome) add('outcome = ?', f.outcome);
  if (f.restrictive) add('restrictive = 1');
  if (f.since) add('event_date >= ?', f.since);
  if (f.until) add('event_date <= ?', f.until);
  if (f.q) add("(title LIKE ? ESCAPE '\\' OR project_name LIKE ? ESCAPE '\\')", ...Array(2).fill(`%${f.q.replace(/[\\%_]/g, '\\$&')}%`));
  if (embargoDays > 0) add('(event_date IS NULL OR event_date <= ?)', addDays(today(), -embargoDays));
  return { sql: sql.join(' AND '), args };
}

export function listRecords(db, filters, { limit = 25, offset = 0, embargoDays = 0 } = {}) {
  const w = where(filters, embargoDays);
  const total = db.prepare(`SELECT COUNT(*) AS n FROM records WHERE ${w.sql}`).get(...w.args).n;
  const rows = db.prepare(`SELECT * FROM records WHERE ${w.sql} ORDER BY event_date DESC, id DESC LIMIT ? OFFSET ?`).all(...w.args, limit, offset);
  const all = embargoDays > 0 ? db.prepare(`SELECT COUNT(*) AS n FROM records WHERE ${where(filters, 0).sql}`).get(...where(filters, 0).args).n : total;
  return { total, withheld: all - total, rows: rows.map(present) };
}

export function getRecord(db, id, embargoDays = 0) {
  const r = db.prepare(`SELECT * FROM records WHERE id = ? AND category IN (${SITING.map(() => '?').join(', ')})`).get(id, ...SITING);
  if (!r) return null;
  if (embargoDays > 0 && r.event_date && r.event_date > addDays(today(), -embargoDays)) return { embargoed: true };
  return { ...present(r), actions: db.prepare('SELECT date, body, action, result, tally FROM actions WHERE record_id = ? ORDER BY date, external_id').all(id) };
}

/** Hearings on a future agenda. */
export function upcoming(db, filters) {
  const w = where(filters, 0);
  return db.prepare(`SELECT * FROM records WHERE ${w.sql} AND agenda_date >= ? ORDER BY agenda_date LIMIT 100`).all(...w.args, today()).map(present);
}

const quarter = (d) => `${d.slice(0, 4)}-Q${Math.floor((Number(d.slice(5, 7)) - 1) / 3) + 1}`;

/** Public headline numbers. Counts only — safe to show without the embargo. */
export function summary(db) {
  const inS = `category IN (${SITING.map(() => '?').join(', ')})`;
  const since12 = addDays(today(), -365);
  const prev12 = addDays(today(), -730);
  const one = (sql, ...a) => db.prepare(sql).get(...SITING, ...a);
  const rows = db.prepare(`SELECT event_date, category, restrictive FROM records WHERE ${inS} AND event_date >= ?`).all(...SITING, addDays(today(), -365 * 4));
  const byQuarter = new Map();
  for (const r of rows) {
    if (r.event_date > today()) continue;
    const q = quarter(r.event_date);
    const b = byQuarter.get(q) || { quarter: q, project: 0, policy: 0, incentive: 0, utility: 0, restrictive: 0 };
    b[r.category] += 1;
    b.restrictive += r.restrictive;
    byQuarter.set(q, b);
  }
  return {
    coverage: { jurisdictions: JURISDICTIONS.length, states: STATES.length, last_sync: db.prepare('SELECT MAX(last_ok) AS t FROM sync').get().t },
    totals: {
      records: one(`SELECT COUNT(*) AS n FROM records WHERE ${inS}`).n,
      last_12_months: one(`SELECT COUNT(*) AS n FROM records WHERE ${inS} AND event_date >= ?`, since12).n,
      prior_12_months: one(`SELECT COUNT(*) AS n FROM records WHERE ${inS} AND event_date >= ? AND event_date < ?`, prev12, since12).n,
      restrictive_last_12_months: one(`SELECT COUNT(*) AS n FROM records WHERE ${inS} AND restrictive = 1 AND event_date >= ?`, since12).n,
      restrictive_prior_12_months: one(`SELECT COUNT(*) AS n FROM records WHERE ${inS} AND restrictive = 1 AND event_date >= ? AND event_date < ?`, prev12, since12).n,
      projects_last_12_months: one(`SELECT COUNT(*) AS n FROM records WHERE ${inS} AND category = 'project' AND event_date >= ?`, since12).n,
      acres_last_12_months: one(`SELECT COALESCE(SUM(acres), 0) AS n FROM records WHERE ${inS} AND category = 'project' AND event_date >= ?`, since12).n,
      upcoming_hearings: one(`SELECT COUNT(*) AS n FROM records WHERE ${inS} AND agenda_date >= ?`, today()).n,
    },
    by_quarter: [...byQuarter.values()].sort((a, b) => (a.quarter < b.quarter ? -1 : 1)),
    by_state: db.prepare(`SELECT state, COUNT(*) AS records, SUM(category = 'project') AS projects, SUM(restrictive) AS restrictive FROM records WHERE ${inS} AND event_date >= ? GROUP BY state ORDER BY records DESC`).all(...SITING, since12),
    project_outcomes: db.prepare(`SELECT outcome, COUNT(*) AS n FROM records WHERE category = 'project' AND event_date >= ? GROUP BY outcome ORDER BY n DESC`).all(prev12),
  };
}

export function coverage(db) {
  const sync = new Map(db.prepare('SELECT * FROM sync').all().map((s) => [s.jurisdiction, s]));
  const counts = new Map(db.prepare(`SELECT jurisdiction, COUNT(*) AS n, MAX(event_date) AS latest FROM records WHERE category IN (${SITING.map(() => '?').join(', ')}) GROUP BY jurisdiction`).all(...SITING).map((c) => [c.jurisdiction, c]));
  return JURISDICTIONS.map((j) => ({
    code: j.client, name: j.name, state: j.state, kind: j.kind,
    records: counts.get(j.client)?.n || 0,
    latest_activity: counts.get(j.client)?.latest || null,
    last_synced: sync.get(j.client)?.last_ok || null,
    healthy: !sync.get(j.client)?.last_error,
  }));
}

export const dimensions = () => ({ categories: Object.fromEntries(SITING.map((c) => [c, CATEGORIES[c]])), outcomes: OUTCOMES, states: STATES });

// ---- Watches: a saved filter with a private Atom feed ----

export function createWatch(db, userId, name, filters, max) {
  const n = db.prepare('SELECT COUNT(*) AS n FROM watches WHERE user_id = ?').get(userId).n;
  if (n >= max) throw new FilterError(max ? `Your plan allows ${max} watches.` : 'Watches are available on the Pro and Team plans.');
  const token = crypto.randomBytes(24).toString('base64url');
  const clean = String(name || '').trim().slice(0, 60) || 'Untitled watch';
  const id = db.prepare('INSERT INTO watches (user_id, name, filters, feed_token, created_at) VALUES (?, ?, ?, ?, ?)').run(userId, clean, JSON.stringify(filters), token, new Date().toISOString()).lastInsertRowid;
  return { id: Number(id), name: clean, filters, feed_token: token };
}
export const listWatches = (db, userId) => db.prepare('SELECT id, name, filters, feed_token, created_at FROM watches WHERE user_id = ? ORDER BY id DESC').all(userId).map((w) => ({ ...w, filters: JSON.parse(w.filters) }));
export const deleteWatch = (db, userId, id) => db.prepare('DELETE FROM watches WHERE id = ? AND user_id = ?').run(id, userId).changes > 0;
export const watchByToken = (db, token) => {
  const w = db.prepare('SELECT w.*, u.plan FROM watches w JOIN users u ON u.id = w.user_id WHERE w.feed_token = ?').get(token);
  return w ? { ...w, filters: JSON.parse(w.filters) } : null;
};

const xml = (s) => String(s ?? '').replace(/[<>&"']/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' })[c]);

export function atomFeed(watch, rows, baseUrl) {
  const updated = new Date().toISOString();
  const entries = rows.map((r) => `  <entry>
    <id>${baseUrl}/record/${r.id}</id>
    <title>${xml(`${r.jurisdiction.name}, ${r.jurisdiction.state}: ${CATEGORIES[r.category]} — ${OUTCOMES[r.outcome]}`)}</title>
    <link href="${xml(`${baseUrl}/record/${r.id}`)}"/>
    <updated>${r.event_date || updated.slice(0, 10)}T00:00:00Z</updated>
    <summary>${xml(r.title.slice(0, 600))}</summary>
  </entry>`).join('\n');
  return `<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>${baseUrl}/feeds/${xml(watch.feed_token)}</id>
  <title>${xml(`Siteline watch: ${watch.name}`)}</title>
  <updated>${updated}</updated>
${entries}
</feed>
`;
}

const cell = (v) => (v === null || v === undefined ? '' : /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
export function recordsCsv(rows) {
  const cols = ['id', 'event_date', 'state', 'jurisdiction', 'category', 'restrictive', 'outcome', 'project_name', 'case_number', 'acres', 'square_feet', 'mw', 'body', 'local_status', 'title', 'source_url'];
  const flat = rows.map((r) => ({ ...r, state: r.jurisdiction.state, jurisdiction: r.jurisdiction.name, title: r.title.replace(/\s+/g, ' ') }));
  return `${[cols.join(','), ...flat.map((r) => cols.map((c) => cell(r[c])).join(','))].join('\n')}\n`;
}
