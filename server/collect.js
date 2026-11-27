// Collection run: pull matching items and their action history for every jurisdiction.
//   node server/collect.js               full sync
//   node server/collect.js --only=mesa,phoenix
//   node server/collect.js --reclassify  re-derive fields from stored text
import { pathToFileURL } from 'node:url';
import { config } from './config.js';
import { SITING, categorize } from './classify.js';
import { fetchHistory, fetchMatters } from './collectors/legistar.js';
import { openDb } from './db.js';
import { JURISDICTIONS } from './jurisdictions.js';
import { markSync, reclassify, saveMatter } from './store.js';

export async function runCollection(db, { only = null, log = console.log } = {}) {
  const summary = { jurisdictions: 0, matters: 0, added: 0, errors: [] };
  for (const jur of JURISDICTIONS.filter((x) => !only || only.includes(x.client))) {
    try {
      const matters = await fetchMatters(jur.client);
      for (const m of matters) {
        // Action history costs one request per item, so only fetch it for real siting records.
        let history = [];
        if (SITING.includes(categorize(m).category)) {
          try {
            history = await fetchHistory(jur.client, m.external_id);
          } catch (err) {
            summary.errors.push(`${jur.client}/${m.external_id} history: ${err.message}`);
          }
        }
        if (saveMatter(db, jur, m, history)) summary.added++;
      }
      markSync(db, jur.client, { ok: true, matters: matters.length });
      summary.jurisdictions++;
      summary.matters += matters.length;
      log(`[collect] ${jur.client}: ${matters.length}`);
    } catch (err) {
      markSync(db, jur.client, { ok: false, error: err.message });
      summary.errors.push(`${jur.client}: ${err.message}`);
      log(`[collect] ${jur.client}: FAILED ${err.message}`);
    }
  }
  log(`[collect] done: ${summary.matters} items from ${summary.jurisdictions} jurisdictions, ${summary.added} new, ${summary.errors.length} errors`);
  return summary;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const db = openDb(config.dbPath);
  if (args.includes('--reclassify')) console.log(`Reclassified ${reclassify(db)} records.`);
  else {
    const onlyArg = args.find((a) => a.startsWith('--only='));
    const s = await runCollection(db, { only: onlyArg ? onlyArg.slice(7).split(',') : null });
    process.exitCode = s.jurisdictions ? 0 : 1;
  }
  db.close();
}
