// Collection run: pull every source, store raw series, recompute signals.
//   node server/collect.js                 full run
//   node server/collect.js --only=npm,hf   subset of sources (pypi,npm,hn,hf)
//   node server/collect.js --signals-only  recompute from stored data
import { pathToFileURL } from 'node:url';
import { config } from './config.js';
import { PROJECTS } from './catalog.js';
import { openDb, today } from './db.js';
import { upsertMetric, replaceMetric, recomputeSignals, saveHfSnapshot } from './store.js';
import { fetchPypiDaily } from './collectors/pypi.js';
import { fetchNpmDaily } from './collectors/npm.js';
import { fetchHnDaily } from './collectors/hackernews.js';
import { fetchHfModels } from './collectors/huggingface.js';

export async function runCollection(db, { only = ['pypi', 'npm', 'hn', 'hf'], log = console.log } = {}) {
  const startedAt = new Date().toISOString();
  const runId = db.prepare('INSERT INTO runs (started_at) VALUES (?)').run(startedAt).lastInsertRowid;
  const summary = { sources: {}, errors: [] };
  const note = (src, key) => {
    summary.sources[src] ??= { ok: 0, missing: [], failed: [] };
    return summary.sources[src][key];
  };
  const record = (src, slug, result) => {
    note(src, 'ok');
    if (result === 'ok') summary.sources[src].ok++;
    else summary.sources[src][result].push(slug);
  };

  async function each(src, field, fn) {
    for (const p of PROJECTS.filter((x) => x[field])) {
      try {
        record(src, p.slug, (await fn(p)) ? 'ok' : 'missing');
      } catch (err) {
        record(src, p.slug, 'failed');
        summary.errors.push(`${src}:${p.slug}: ${err.message}`);
      }
    }
    log(`[collect] ${src}: ${JSON.stringify(summary.sources[src])}`);
  }

  if (only.includes('npm')) {
    await each('npm', 'npm', async (p) => {
      const pts = await fetchNpmDaily(p.npm, config.historyDays);
      if (!pts?.length) return false;
      replaceMetric(db, p.slug, 'npm_downloads', pts);
      return true;
    });
  }
  if (only.includes('pypi')) {
    await each('pypi', 'pypi', async (p) => {
      const pts = await fetchPypiDaily(p.pypi);
      if (!pts?.length) return false;
      replaceMetric(db, p.slug, 'pypi_downloads', pts);
      return true;
    });
  }
  if (only.includes('hn')) {
    await each('hn', 'hn', async (p) => {
      const rows = await fetchHnDaily(p.hn, config.historyDays);
      upsertMetric(db, p.slug, 'hn_stories', rows.map((r) => ({ date: r.date, value: r.stories })));
      upsertMetric(db, p.slug, 'hn_points', rows.map((r) => ({ date: r.date, value: r.points })));
      return true;
    });
  }
  if (only.includes('hf')) {
    try {
      const models = await fetchHfModels(config.hfModelLimit);
      saveHfSnapshot(db, today(), models);
      summary.sources.hf = { ok: models.length };
    } catch (err) {
      summary.sources.hf = { ok: 0 };
      summary.errors.push(`hf: ${err.message}`);
    }
    log(`[collect] hf: ${JSON.stringify(summary.sources.hf)}`);
  }

  summary.signals = recomputeSignals(db);
  // A run is healthy when nothing threw; unknown packages are reported, not fatal.
  const ok = summary.errors.length === 0;
  db.prepare('UPDATE runs SET finished_at = ?, ok = ?, summary = ? WHERE id = ?').run(new Date().toISOString(), ok ? 1 : 0, JSON.stringify(summary), runId);
  log(`[collect] signals: ${summary.signals.count} rows, as of ${JSON.stringify(summary.signals.asOf)}; errors: ${summary.errors.length}`);
  return { ok, summary };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const db = openDb(config.dbPath);
  if (args.includes('--signals-only')) {
    console.log(recomputeSignals(db));
  } else {
    const onlyArg = args.find((a) => a.startsWith('--only='));
    const { ok, summary } = await runCollection(db, onlyArg ? { only: onlyArg.slice(7).split(',') } : {});
    for (const e of summary.errors) console.error(`[collect] ERROR ${e}`);
    process.exitCode = ok ? 0 : 1;
  }
  db.close();
}
