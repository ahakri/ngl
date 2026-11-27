// Assembles API payloads from stored signals and series.
import { CATEGORIES, ECOSYSTEMS, PROJECTS, categoryBySlug, projectBySlug } from './catalog.js';
import { addDays } from './db.js';
import { shareSeries } from './pipeline/signals.js';
import { categoryMembers, gapDates, listBreaks, loadCleanSeries, loadSeries, regimeStart } from './store.js';

const MIN_MOVER_VOLUME = 10000; // trailing-28-day downloads

const decorate = (row) => {
  const p = projectBySlug.get(row.project);
  return {
    project: row.project,
    name: p.name,
    vendor: p.vendor,
    category: p.category,
    ecosystem: row.ecosystem,
    package: p[row.ecosystem],
    as_of: row.as_of,
    downloads_7d: row.d7,
    downloads_28d: row.d28,
    growth_7d: row.growth_7d,
    growth_28d: row.growth_28d,
    growth_12w: row.growth_12w,
    acceleration: row.accel,
    share: row.share,
    share_delta_28d: row.share_delta_28d,
    momentum: row.momentum,
    rank: row.rank,
    rank_delta_28d: row.rank_delta_28d,
    breakout: Boolean(row.breakout),
  };
};

const known = (rows) => rows.filter((r) => projectBySlug.has(r.project));

export function asOfDates(db) {
  const rows = db.prepare('SELECT ecosystem, MAX(as_of) AS as_of FROM signals GROUP BY ecosystem').all();
  return Object.fromEntries(rows.map((r) => [r.ecosystem, r.as_of]));
}

export function meta(db) {
  const run = db.prepare('SELECT started_at, finished_at, ok FROM runs WHERE finished_at IS NOT NULL ORDER BY id DESC LIMIT 1').get();
  const hf = db.prepare('SELECT MAX(date) AS date, COUNT(DISTINCT date) AS snapshots FROM hf_model_daily').get();
  return {
    as_of: asOfDates(db),
    ecosystems: ECOSYSTEMS,
    categories: CATEGORIES.map((c) => ({
      slug: c.slug,
      name: c.name,
      blurb: c.blurb,
      projects: c.projects.length,
      ecosystems: ECOSYSTEMS.filter((e) => c.projects.some((p) => p[e])),
    })),
    coverage: {
      projects: PROJECTS.length,
      series: db.prepare("SELECT COUNT(DISTINCT project || metric) AS n FROM metrics").get().n,
      data_points: db.prepare('SELECT COUNT(*) AS n FROM metrics').get().n,
      hf_models: db.prepare('SELECT COUNT(*) AS n FROM hf_models').get().n,
      hf_snapshot: hf.date,
      hf_snapshots: hf.snapshots,
    },
    quality: {
      structural_breaks: listBreaks(db),
      imputed_days: Object.fromEntries(ECOSYSTEMS.map((e) => [e, [...gapDates(db, e)].sort()])),
    },
    last_run: run ? { finished_at: run.finished_at, ok: Boolean(run.ok) } : null,
  };
}

export function allSignals(db, { ecosystem, category } = {}) {
  let rows = known(db.prepare('SELECT * FROM signals').all()).map(decorate);
  if (ecosystem) rows = rows.filter((r) => r.ecosystem === ecosystem);
  if (category) rows = rows.filter((r) => r.category === category);
  return rows.sort((a, b) => b.downloads_28d - a.downloads_28d);
}

export function movers(db, { ecosystem, direction = 'up', limit = 10 } = {}) {
  const rows = allSignals(db, { ecosystem }).filter((r) => r.momentum !== null && r.downloads_28d >= MIN_MOVER_VOLUME);
  rows.sort((a, b) => (direction === 'down' ? a.momentum - b.momentum : b.momentum - a.momentum));
  return rows.slice(0, limit);
}

export function categoryView(db, slug, ecosystem, weeks) {
  const category = categoryBySlug.get(slug);
  if (!category) return null;
  const asOf = asOfDates(db)[ecosystem];
  const leaderboard = allSignals(db, { ecosystem, category: slug }).sort((a, b) => a.rank - b.rank);
  if (!asOf || !leaderboard.length) return { category: { slug, name: category.name, blurb: category.blurb }, ecosystem, as_of: asOf || null, leaderboard: [], share: { dates: [], series: [] } };
  const regime = regimeStart(db, ecosystem);
  const share = shareSeries(categoryMembers(db, category, ecosystem), asOf, weeks, regime);
  return {
    category: { slug, name: category.name, blurb: category.blurb },
    ecosystem,
    as_of: asOf,
    regime_start: regime,
    total_downloads_28d: leaderboard.reduce((s, r) => s + r.downloads_28d, 0),
    leaderboard,
    share: {
      dates: share.dates,
      series: share.series.map((s) => ({ project: s.slug, name: projectBySlug.get(s.slug).name, share: s.share.map((x) => Math.round(x * 1e5) / 1e5), downloads_28d: s.volume })),
    },
  };
}

function weekly(series, weeks) {
  const dates = [...series.keys()].sort();
  if (!dates.length) return [];
  const end = new Date().toISOString().slice(0, 10);
  const out = [];
  for (let w = weeks - 1; w >= 0; w--) {
    const d = addDays(end, -7 * w);
    let v = 0;
    for (let i = 0; i < 7; i++) v += series.get(addDays(d, -i)) || 0;
    out.push({ week_ending: d, value: v });
  }
  return out;
}

export function projectView(db, slug, historyDays) {
  const p = projectBySlug.get(slug);
  if (!p) return null;
  const category = categoryBySlug.get(p.category);
  const signals = known(db.prepare('SELECT * FROM signals WHERE project = ?').all(slug)).map(decorate);
  const series = {};
  for (const eco of ECOSYSTEMS) {
    if (!p[eco]) continue;
    const asOf = asOfDates(db)[eco];
    if (!asOf) continue;
    const since = addDays(asOf, -historyDays + 1);
    const clean = loadCleanSeries(db, slug, eco);
    series[eco] = [...clean].filter(([d]) => d >= since && d <= asOf).map(([date, downloads]) => ({ date, downloads }));
  }
  const weeks = Math.min(52, Math.ceil(historyDays / 7));
  return {
    project: { slug, name: p.name, vendor: p.vendor, category: p.category, category_name: category.name, packages: { pypi: p.pypi || null, npm: p.npm || null }, hn_query: p.hn || null },
    signals,
    series,
    attention: p.hn ? { source: 'Hacker News stories', weekly: weekly(loadSeries(db, slug, 'hn_stories'), weeks) } : null,
    quality: { structural_breaks: listBreaks(db).filter((b) => p[b.ecosystem]) },
  };
}

// ---- Hugging Face ----

const hfDates = (db) => db.prepare('SELECT DISTINCT date FROM hf_model_daily ORDER BY date DESC').all().map((r) => r.date);

/** Snapshot to compare against: the oldest one within `days`, if a different day exists. */
function baseline(dates, days) {
  if (dates.length < 2) return null;
  const floor = addDays(dates[0], -days);
  return dates.filter((d) => d < dates[0] && d >= floor).at(-1) || null;
}

export function hfAggregate(db, dim, limit) {
  const dates = hfDates(db);
  if (!dates.length) return { as_of: null, rows: [] };
  const [latest] = dates;
  const base = baseline(dates, 30);
  const total = db.prepare('SELECT SUM(downloads_30d) AS t FROM hf_agg_daily WHERE dim = ? AND date = ?').get(dim, latest).t || 0;
  const baseTotal = base ? db.prepare('SELECT SUM(downloads_30d) AS t FROM hf_agg_daily WHERE dim = ? AND date = ?').get(dim, base).t || 0 : 0;
  const prev = base ? new Map(db.prepare('SELECT key, downloads_30d FROM hf_agg_daily WHERE dim = ? AND date = ?').all(dim, base).map((r) => [r.key, r.downloads_30d])) : new Map();
  const rows = db.prepare('SELECT key, downloads_30d, models, likes FROM hf_agg_daily WHERE dim = ? AND date = ? ORDER BY downloads_30d DESC LIMIT ?').all(dim, latest, limit);
  return {
    as_of: latest,
    compared_to: base,
    total_downloads_30d: total,
    rows: rows.map((r, i) => {
      const before = prev.get(r.key);
      return {
        rank: i + 1,
        [dim]: r.key,
        downloads_30d: r.downloads_30d,
        models: r.models,
        likes: r.likes,
        share: total ? r.downloads_30d / total : null,
        share_delta: base && before !== undefined && baseTotal ? r.downloads_30d / total - before / baseTotal : null,
      };
    }),
  };
}

export function hfModels(db, sort, limit) {
  const dates = hfDates(db);
  if (!dates.length) return { as_of: null, rows: [] };
  const [latest] = dates;
  const base = baseline(dates, 7);
  const order = sort === 'trending' ? 'd.trending DESC' : sort === 'likes' ? 'd.likes DESC' : 'd.downloads_30d DESC';
  const rows = db.prepare(`SELECT m.id, m.org, m.task, m.library, m.created_at, d.downloads_30d, d.likes, d.trending, b.downloads_30d AS base_downloads
    FROM hf_model_daily d JOIN hf_models m ON m.id = d.id
    LEFT JOIN hf_model_daily b ON b.id = d.id AND b.date = ?
    WHERE d.date = ? AND (? <> 'trending' OR d.trending IS NOT NULL) ORDER BY ${order} LIMIT ?`).all(base, latest, sort, limit);
  return {
    as_of: latest,
    compared_to: base,
    rows: rows.map((r, i) => ({
      rank: i + 1,
      id: r.id,
      org: r.org,
      task: r.task,
      library: r.library,
      created_at: r.created_at,
      downloads_30d: r.downloads_30d,
      likes: r.likes,
      trending_score: r.trending,
      downloads_change: r.base_downloads ? r.downloads_30d / r.base_downloads - 1 : null,
    })),
  };
}

// ---- CSV ----

const cell = (v) => (v === null || v === undefined ? '' : /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
export const toCsv = (cols, rows) => [cols.join(','), ...rows.map((r) => cols.map((c) => cell(r[c])).join(','))].join('\n') + '\n';
