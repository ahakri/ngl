// Server entry point.
import { config } from './config.js';
import { openDb } from './db.js';
import { buildApp } from './app.js';

const db = openDb(config.dbPath);
const app = buildApp(db, { logger: { level: config.env === 'production' ? 'info' : 'warn' } });

await app.listen({ port: config.port, host: config.host });
console.log(`Rangefinder listening on ${config.publicUrl}`);
if (!config.adminEmails.length) console.log('No ADMIN_EMAILS set: flagged submissions will wait in the queue with nobody to review them.');

for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, async () => {
    await app.close();
    db.close();
    process.exit(0);
  });
}
