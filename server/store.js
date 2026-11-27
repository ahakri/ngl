// Persistence for siting records and their action history.
import { classify } from './classify.js';
import { tx } from './db.js';

const FIELDS = ['file', 'name', 'title', 'type_name', 'status_name', 'body_name', 'intro_date', 'agenda_date', 'passed_date', 'modified_utc', 'url'];
const DERIVED = ['category', 'restrictive', 'outcome', 'acres', 'square_feet', 'mw', 'project_name', 'case_number', 'staff_recommendation', 'event_date'];

function derive(matter, history) {
  const c = classify(matter, history);
  const dates = [history.at(-1)?.date, matter.passed_date, matter.agenda_date, matter.intro_date].filter(Boolean).sort();
  return { ...c, restrictive: c.restrictive ? 1 : 0, event_date: dates.at(-1) || null };
}

/** Insert or update one item with its history. Returns true when it is new. */
export function saveMatter(db, jur, matter, history = [], now = new Date().toISOString()) {
  const d = derive(matter, history);
  return tx(db, () => {
    const existing = db.prepare('SELECT id FROM records WHERE jurisdiction = ? AND external_id = ?').get(jur.client, matter.external_id);
    let id = existing?.id;
    if (id) {
      db.prepare(`UPDATE records SET ${[...FIELDS, ...DERIVED].map((f) => `${f} = ?`).join(', ')} WHERE id = ?`)
        .run(...FIELDS.map((f) => matter[f] ?? null), ...DERIVED.map((f) => d[f] ?? null), id);
    } else {
      id = Number(db.prepare(`INSERT INTO records (jurisdiction, state, external_id, ${[...FIELDS, ...DERIVED].join(', ')}, first_seen) VALUES (?, ?, ?, ${[...FIELDS, ...DERIVED].map(() => '?').join(', ')}, ?)`)
        .run(jur.client, jur.state, matter.external_id, ...FIELDS.map((f) => matter[f] ?? null), ...DERIVED.map((f) => d[f] ?? null), now).lastInsertRowid);
    }
    const up = db.prepare('INSERT OR REPLACE INTO actions (record_id, external_id, date, body, action, result, tally) VALUES (?, ?, ?, ?, ?, ?, ?)');
    for (const h of history) up.run(id, h.external_id, h.date, h.body, h.action, h.result, h.tally);
    return !existing;
  });
}

/** Re-run classification over stored rows (after the rules change). */
export function reclassify(db) {
  const rows = db.prepare('SELECT * FROM records').all();
  const hist = db.prepare('SELECT * FROM actions WHERE record_id = ? ORDER BY date').all.bind(db.prepare('SELECT * FROM actions WHERE record_id = ? ORDER BY date'));
  tx(db, () => {
    for (const r of rows) {
      const d = derive(r, hist(r.id));
      db.prepare(`UPDATE records SET ${DERIVED.map((f) => `${f} = ?`).join(', ')} WHERE id = ?`).run(...DERIVED.map((f) => d[f] ?? null), r.id);
    }
  });
  return rows.length;
}

export const markSync = (db, client, { ok, error = null, matters = 0 }) =>
  db.prepare(`INSERT INTO sync (jurisdiction, last_ok, last_error, matters) VALUES (?, ?, ?, ?)
    ON CONFLICT (jurisdiction) DO UPDATE SET last_ok = COALESCE(excluded.last_ok, last_ok), last_error = excluded.last_error, matters = CASE WHEN excluded.last_ok IS NULL THEN matters ELSE excluded.matters END`)
    .run(client, ok ? new Date().toISOString() : null, error, matters);
