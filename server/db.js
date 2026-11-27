// SQLite storage (node:sqlite — no native build step). One file, WAL mode.
import { DatabaseSync } from 'node:sqlite';
import fs from 'node:fs';
import path from 'node:path';

const SCHEMA = `
CREATE TABLE IF NOT EXISTS records (
  id INTEGER PRIMARY KEY,
  jurisdiction TEXT NOT NULL,       -- Legistar client code
  state TEXT NOT NULL,
  external_id TEXT NOT NULL,
  file TEXT, name TEXT, title TEXT NOT NULL,
  type_name TEXT, status_name TEXT, body_name TEXT,
  intro_date TEXT, agenda_date TEXT, passed_date TEXT,
  modified_utc TEXT, url TEXT NOT NULL,
  -- derived by classify.js
  category TEXT NOT NULL, restrictive INTEGER NOT NULL DEFAULT 0, outcome TEXT NOT NULL,
  acres REAL, square_feet REAL, mw REAL,
  project_name TEXT, case_number TEXT, staff_recommendation TEXT,
  event_date TEXT,                  -- latest known activity: last action, else agenda, else intro
  first_seen TEXT NOT NULL,
  UNIQUE (jurisdiction, external_id)
);
CREATE INDEX IF NOT EXISTS idx_records_event ON records(event_date);
CREATE INDEX IF NOT EXISTS idx_records_cat ON records(category, state);

CREATE TABLE IF NOT EXISTS actions (
  record_id INTEGER NOT NULL REFERENCES records(id) ON DELETE CASCADE,
  external_id TEXT NOT NULL,
  date TEXT NOT NULL, body TEXT, action TEXT, result TEXT, tally TEXT,
  PRIMARY KEY (record_id, external_id)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS sync (
  jurisdiction TEXT PRIMARY KEY,
  last_ok TEXT, last_error TEXT, matters INTEGER NOT NULL DEFAULT 0
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS watches (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  filters TEXT NOT NULL,            -- JSON: { state, jurisdiction, category, q }
  feed_token TEXT NOT NULL UNIQUE,  -- secret in the private feed URL
  created_at TEXT NOT NULL
);

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
