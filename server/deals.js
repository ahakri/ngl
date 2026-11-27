// Persistence and access rules for deal submissions.
import { screen } from './benchmarks.js';
import { config } from './config.js';
import { CONTRIBUTOR_DAYS } from './plans.js';

const COLUMNS = ['sport', 'level', 'class_year', 'role', 'region', 'followers', 'payer_type', 'industry', 'deal_type', 'deliverables', 'duration_months', 'cash_usd', 'in_kind_usd', 'total_usd', 'exclusive', 'has_agent', 'clearance', 'signed_quarter'];
const MAX_PER_30_DAYS = 12;

export class DealError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.status = status;
  }
}

// The published dataset is read on almost every request and changes rarely.
let cache = { version: -1, rows: [] };
let version = 0;
const touch = () => { version++; };

/** Every approved deal. Cached until a write changes the dataset. */
export function publishedDeals(db) {
  if (cache.version !== version) cache = { version, rows: db.prepare("SELECT * FROM deals WHERE status = 'approved'").all() };
  return cache.rows;
}

export function submitDeal(db, userId, deal, { isDemo = false, now = new Date() } = {}) {
  if (!isDemo) {
    const since = new Date(now - 30 * 86400e3).toISOString();
    const recent = db.prepare('SELECT COUNT(*) AS n FROM deals WHERE user_id = ? AND created_at > ?').get(userId, since).n;
    if (recent >= MAX_PER_30_DAYS) throw new DealError(`You can submit up to ${MAX_PER_30_DAYS} deals every 30 days.`, 429);
    const twin = db.prepare(`SELECT 1 FROM deals WHERE user_id = ? AND status <> 'rejected' AND sport = ? AND deal_type = ? AND payer_type = ? AND total_usd = ? AND signed_quarter = ?`)
      .get(userId, deal.sport, deal.deal_type, deal.payer_type, deal.total_usd, deal.signed_quarter);
    if (twin) throw new DealError('You have already submitted this deal.', 409);
  }
  const flags = isDemo ? [] : screen(deal, publishedDeals(db));
  const status = flags.length || (!config.autoApprove && !isDemo) ? 'pending' : 'approved';
  const id = db.prepare(`INSERT INTO deals (user_id, status, flags, is_demo, created_at, ${COLUMNS.join(', ')}) VALUES (?, ?, ?, ?, ?, ${COLUMNS.map(() => '?').join(', ')})`)
    .run(userId, status, JSON.stringify(flags), isDemo ? 1 : 0, now.toISOString(), ...COLUMNS.map((c) => deal[c] ?? null)).lastInsertRowid;
  touch();
  return { id: Number(id), status, flags };
}

const mine = (r) => ({ id: r.id, status: r.status, created_at: r.created_at, sport: r.sport, deal_type: r.deal_type, payer_type: r.payer_type, total_usd: r.total_usd, signed_quarter: r.signed_quarter, verified: Boolean(r.verified) });

export const myDeals = (db, userId) => db.prepare('SELECT * FROM deals WHERE user_id = ? ORDER BY id DESC').all(userId).map(mine);

export function withdrawDeal(db, userId, id) {
  const ok = db.prepare('DELETE FROM deals WHERE id = ? AND user_id = ?').run(id, userId).changes > 0;
  if (ok) touch();
  return ok;
}

/** True while the user has a non-rejected submission from the last 12 months. */
export function isContributor(db, userId, now = new Date()) {
  const since = new Date(now - CONTRIBUTOR_DAYS * 86400e3).toISOString();
  return Boolean(db.prepare("SELECT 1 FROM deals WHERE user_id = ? AND status <> 'rejected' AND created_at > ? LIMIT 1").get(userId, since));
}

export const reviewQueue = (db) =>
  db.prepare("SELECT * FROM deals WHERE status = 'pending' ORDER BY id").all().map((r) => ({ ...r, flags: JSON.parse(r.flags), user_id: undefined }));

/** Moderator decision: approve, reject, or approve and mark as verified. */
export function reviewDeal(db, id, action) {
  const set = { approve: ["status = 'approved'"], verify: ["status = 'approved'", 'verified = 1'], reject: ["status = 'rejected'"] }[action];
  if (!set) throw new DealError('Unknown action.');
  const ok = db.prepare(`UPDATE deals SET ${set.join(', ')}, reviewed_at = ? WHERE id = ?`).run(new Date().toISOString(), id).changes > 0;
  if (ok) touch();
  return ok;
}

export function datasetStats(db) {
  const row = db.prepare(`SELECT COUNT(*) AS deals, COALESCE(SUM(total_usd), 0) AS value, COUNT(DISTINCT sport) AS sports,
    COALESCE(SUM(is_demo), 0) AS demo, COALESCE(SUM(verified), 0) AS verified, MAX(created_at) AS latest FROM deals WHERE status = 'approved'`).get();
  return { deals: row.deals, total_value_usd: row.value, sports: row.sports, verified: row.verified, latest_submission: row.latest, demo_data: row.demo > 0 };
}

/** Remove synthetic sample data. */
export function purgeDemo(db) {
  const n = db.prepare('DELETE FROM deals WHERE is_demo = 1').run().changes;
  touch();
  return n;
}
