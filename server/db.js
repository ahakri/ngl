// SQLite storage (node:sqlite — no native build step). One file, WAL mode.
import { DatabaseSync } from 'node:sqlite';
import fs from 'node:fs';
import path from 'node:path';

const SCHEMA = `
CREATE TABLE IF NOT EXISTS deals (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
  status TEXT NOT NULL DEFAULT 'approved',   -- approved | pending | rejected
  flags TEXT NOT NULL DEFAULT '[]',          -- JSON list of screening reasons
  verified INTEGER NOT NULL DEFAULT 0,       -- a moderator has seen proof
  is_demo INTEGER NOT NULL DEFAULT 0,        -- synthetic sample data, never real
  created_at TEXT NOT NULL,
  reviewed_at TEXT,
  -- athlete context (no name, school or team is ever stored)
  sport TEXT NOT NULL, level TEXT NOT NULL, class_year TEXT NOT NULL, role TEXT, region TEXT NOT NULL,
  followers INTEGER NOT NULL,
  -- the deal (no brand name is ever stored)
  payer_type TEXT NOT NULL, industry TEXT NOT NULL, deal_type TEXT NOT NULL,
  deliverables INTEGER NOT NULL, duration_months INTEGER NOT NULL,
  cash_usd INTEGER NOT NULL, in_kind_usd INTEGER NOT NULL, total_usd INTEGER NOT NULL,
  exclusive INTEGER NOT NULL, has_agent INTEGER NOT NULL,
  clearance TEXT NOT NULL, signed_quarter TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_deals_status ON deals(status);
CREATE INDEX IF NOT EXISTS idx_deals_user ON deals(user_id);

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE COLLATE NOCASE,
  password_hash TEXT NOT NULL,
  plan TEXT NOT NULL DEFAULT 'free',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires_at TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS api_keys (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  prefix TEXT NOT NULL,
  key_hash TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  last_used_at TEXT,
  revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS usage (
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date TEXT NOT NULL,
  requests INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, date)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS stripe_events (
  id TEXT PRIMARY KEY,
  received_at TEXT NOT NULL
) WITHOUT ROWID;

`;

export function openDb(file) {
  if (file !== ':memory:') fs.mkdirSync(path.dirname(file), { recursive: true });
  const db = new DatabaseSync(file);
  db.exec('PRAGMA journal_mode = WAL; PRAGMA foreign_keys = ON; PRAGMA busy_timeout = 5000; PRAGMA synchronous = NORMAL;');
  db.exec(SCHEMA);
  return db;
}

/** Run fn inside a transaction; rolls back on throw. */
export function tx(db, fn) {
  db.exec('BEGIN');
  try {
    const out = fn();
    db.exec('COMMIT');
    return out;
  } catch (err) {
    db.exec('ROLLBACK');
    throw err;
  }
}

export const today = (d = new Date()) => d.toISOString().slice(0, 10);
export const addDays = (date, n) => {
  const d = new Date(`${date}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
};
