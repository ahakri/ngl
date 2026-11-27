// Server entry point: HTTP app + daily collection.
import { config } from './config.js';
import { openDb } from './db.js';
import { buildApp } from './app.js';
import { runCollection } from './collect.js';

const db = openDb(config.dbPath);
const app = buildApp(db, { logger: { level: config.env === 'production' ? 'info' : 'warn' } });

let running = false;
async function collect(reason) {
  if (running) return;
  running = true;
  console.log(`[scheduler] collection started (${reason})`);
  try {
    await runCollection(db, { log: () => {} }).then((s) => console.log(`[scheduler] ${s.matters} items, ${s.added} new, ${s.errors.length} errors`));
  } catch (err) {
    console.error('[scheduler] collection crashed', err);
  } finally {
    running = false;
  }
}

function scheduleDaily() {
  const next = new Date();
  next.setUTCHours(config.collectHourUtc, 0, 0, 0);
  if (next <= new Date()) next.setUTCDate(next.getUTCDate() + 1);
  setTimeout(() => collect('daily').finally(scheduleDaily), next - Date.now()).unref();
}

await app.listen({ port: config.port, host: config.host });
console.log(`Siteline listening on ${config.publicUrl}`);

if (config.schedulerEnabled) {
  if (!db.prepare('SELECT 1 FROM records LIMIT 1').get()) collect('empty database');
  scheduleDaily();
}

for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, async () => {
    await app.close();
    db.close();
    process.exit(0);
  });
}
