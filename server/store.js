// Read/write helpers over the metrics tables, shared by the collector and API.
import { CATEGORIES, ECOSYSTEMS } from './catalog.js';
import { computeCategorySignals, detectBreaks, detectGaps, fillGaps, pickAsOf } from './pipeline/signals.js';
import { addDays, tx } from './db.js';

export function upsertMetric(db, project, metric, points) {
  const stmt = db.prepare(
    'INSERT INTO metrics (project, metric, date, value) VALUES (?, ?, ?, ?) ON CONFLICT (project, metric, date) DO UPDATE SET value = excluded.value',
  );
  tx(db, () => {
    for (const pt of points) stmt.run(project, metric, pt.date, pt.value);
  });
}

/** @returns {Map<string, number>} date → value */
export function loadSeries(db, project, metric, since = '0000-00-00') {
  const rows = db.prepare('SELECT date, value FROM metrics WHERE project = ? AND metric = ? AND date >= ? ORDER BY date').all(project, metric, since);
  return new Map(rows.map((r) => [r.date, r.value]));
}

export function gapDates(db, ecosystem) {
  return new Set(db.prepare('SELECT date FROM gaps WHERE ecosystem = ?').all(ecosystem).map((r) => r.date));
}

/** Download series with upstream outage days imputed — what every signal is computed on. */
export function loadCleanSeries(db, project, ecosystem, gaps = gapDates(db, ecosystem)) {
  return fillGaps(loadSeries(db, project, `${ecosystem}_downloads`), gaps);
}

export function categoryMembers(db, category, ecosystem) {
  const gaps = gapDates(db, ecosystem);
  return category.projects
    .filter((p) => p[ecosystem])
    .map((p) => ({ slug: p.slug, series: loadCleanSeries(db, p.slug, ecosystem, gaps) }))
    .filter((m) => m.series.size);
}

/** Replace all stored points for a series (drops days the source no longer reports). */
export function replaceMetric(db, project, metric, points) {
  tx(db, () => {
    if (points.length) db.prepare('DELETE FROM metrics WHERE project = ? AND metric = ? AND date >= ?').run(project, metric, points[0].date);
  });
  upsertMetric(db, project, metric, points);
}

/** Latest structural break for an ecosystem, or null. */
export function regimeStart(db, ecosystem) {
  return db.prepare('SELECT MAX(date) AS d FROM breaks WHERE ecosystem = ?').get(ecosystem).d || null;
}

export function listBreaks(db) {
  return db.prepare('SELECT ecosystem, date, ratio FROM breaks ORDER BY date').all();
}

function refreshQuality(db, eco) {
  const metric = `${eco}_downloads`;
  const span = db.prepare('SELECT MIN(date) AS a FROM metrics WHERE metric = ?').get(metric);
  if (!span.a) return;
  // Aggregate only over series present for the whole window, so a newly
  // tracked package can't masquerade as a level shift.
  const stable = db.prepare('SELECT project FROM metrics WHERE metric = ? GROUP BY project HAVING MIN(date) <= ?').all(metric, addDays(span.a, 7)).map((r) => r.project);
  const total = (gaps) => {
    const sum = new Map();
    for (const slug of stable) for (const [d, v] of fillGaps(loadSeries(db, slug, metric), gaps)) sum.set(d, (sum.get(d) || 0) + v);
    return sum;
  };
  const gaps = detectGaps(total(new Set()));
  db.prepare('DELETE FROM gaps WHERE ecosystem = ?').run(eco);
  for (const d of gaps) db.prepare('INSERT INTO gaps (ecosystem, date) VALUES (?, ?)').run(eco, d);
  db.prepare('DELETE FROM breaks WHERE ecosystem = ? AND date >= ?').run(eco, span.a);
  for (const b of detectBreaks(total(gaps))) db.prepare('INSERT OR REPLACE INTO breaks (ecosystem, date, ratio) VALUES (?, ?, ?)').run(eco, b.date, b.ratio);
}

/** Recompute every signal row from the stored series. Idempotent. */
export function recomputeSignals(db) {
  const insert = db.prepare(`INSERT INTO signals
    (project, ecosystem, as_of, d7, d28, growth_7d, growth_28d, growth_12w, accel, share, share_delta_28d, momentum, rank, rank_delta_28d, breakout)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`);
  let count = 0;
  const asOfByEco = {};
  tx(db, () => {
    db.exec('DELETE FROM signals');
    for (const eco of ECOSYSTEMS) {
      refreshQuality(db, eco);
      const regime = regimeStart(db, eco);
      const sets = CATEGORIES.map((c) => categoryMembers(db, c, eco));
      const asOf = pickAsOf(sets.flat().map((m) => m.series));
      asOfByEco[eco] = asOf;
      if (!asOf) continue;
      for (const members of sets) {
        for (const r of computeCategorySignals(members, asOf, regime)) {
          insert.run(r.project, eco, r.as_of, r.d7, r.d28, r.growth_7d, r.growth_28d, r.growth_12w, r.accel, r.share, r.share_delta_28d, r.momentum, r.rank, r.rank_delta_28d, r.breakout);
          count++;
        }
      }
    }
  });
  return { count, asOf: asOfByEco };
}

export function saveHfSnapshot(db, date, models) {
  const upModel = db.prepare(`INSERT INTO hf_models (id, org, task, library, created_at, first_seen) VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT (id) DO UPDATE SET task = excluded.task, library = excluded.library`);
  const upDaily = db.prepare(`INSERT INTO hf_model_daily (id, date, downloads_30d, likes, trending) VALUES (?, ?, ?, ?, ?)
    ON CONFLICT (id, date) DO UPDATE SET downloads_30d = excluded.downloads_30d, likes = excluded.likes, trending = excluded.trending`);
  const upAgg = db.prepare(`INSERT INTO hf_agg_daily (dim, key, date, downloads_30d, models, likes) VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT (dim, key, date) DO UPDATE SET downloads_30d = excluded.downloads_30d, models = excluded.models, likes = excluded.likes`);
  tx(db, () => {
    const agg = { org: new Map(), task: new Map() };
    for (const m of models) {
      upModel.run(m.id, m.org, m.task, m.library, m.createdAt, date);
      upDaily.run(m.id, date, m.downloads, m.likes, m.trending);
      for (const [dim, key] of [['org', m.org], ['task', m.task || 'unspecified']]) {
        const a = agg[dim].get(key) || { downloads: 0, models: 0, likes: 0 };
        a.downloads += m.downloads;
        a.models += 1;
        a.likes += m.likes;
        agg[dim].set(key, a);
      }
    }
    db.prepare('DELETE FROM hf_agg_daily WHERE date = ?').run(date);
    for (const dim of ['org', 'task']) for (const [key, a] of agg[dim]) upAgg.run(dim, key, date, a.downloads, a.models, a.likes);
  });
}
