// Server entry point: HTTP app + daily collection scheduler.
import { config } from './config.js';
import { openDb } from './db.js';
import { buildApp } from './app.js';
import { runCollection } from './collect.js';

const db = openDb(config.dbPath);
const app = buildApp(db, { logger: { level: config.env === 'production' ? 'info' : 'warn' } });

let collecting = false;
async function collect(reason) {
  if (collecting) return;
  collecting = true;
  console.log(`[scheduler] collection started (${reason})`);
  try {
    const { ok, summary } = await runCollection(db);
    console.log(`[scheduler] collection ${ok ? 'ok' : 'finished with errors'}: ${summary.errors.slice(0, 5).join('; ')}`);
  } catch (err) {
    console.error('[scheduler] collection crashed', err);
  } finally {
    collecting = false;
  }
}

function scheduleDaily() {
  const next = new Date();
  next.setUTCHours(config.collectHourUtc, 0, 0, 0);
  if (next <= new Date()) next.setUTCDate(next.getUTCDate() + 1);
  setTimeout(() => {
    collect('daily').finally(scheduleDaily);
  }, next - Date.now()).unref();
  console.log(`[scheduler] next collection at ${next.toISOString()}`);
}

await app.listen({ port: config.port, host: config.host });
console.log(`Uptake listening on ${config.publicUrl}`);

if (config.schedulerEnabled) {
  const empty = !db.prepare('SELECT 1 FROM signals LIMIT 1').get();
  if (config.collectOnBoot || empty) collect(empty ? 'empty database' : 'boot');
  scheduleDaily();
}

for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, async () => {
    await app.close();
    db.close();
    process.exit(0);
  });
}
