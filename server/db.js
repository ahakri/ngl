// SQLite storage (node:sqlite — no native build step). One file, WAL mode.
import { DatabaseSync } from 'node:sqlite';
import fs from 'node:fs';
import path from 'node:path';

const SCHEMA = `
CREATE TABLE IF NOT EXISTS metrics (
  project TEXT NOT NULL,          -- catalog slug
  metric  TEXT NOT NULL,          -- pypi_downloads | npm_downloads | hn_stories | hn_points
  date    TEXT NOT NULL,          -- YYYY-MM-DD (UTC)
  value   REAL NOT NULL,
  PRIMARY KEY (project, metric, date)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS signals (
  project      TEXT NOT NULL,
  ecosystem    TEXT NOT NULL,     -- pypi | npm
  as_of        TEXT NOT NULL,
  d7           REAL, d28 REAL,
  growth_7d    REAL, growth_28d REAL, growth_12w REAL,
  accel        REAL,
  share        REAL, share_delta_28d REAL,
  momentum     REAL,
  rank         INTEGER, rank_delta_28d INTEGER,
  breakout     INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (project, ecosystem)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS breaks (
  ecosystem TEXT NOT NULL,
  date TEXT NOT NULL,             -- first day of the new counting regime
  ratio REAL NOT NULL,            -- level after / level before
  PRIMARY KEY (ecosystem, date)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS gaps (
  ecosystem TEXT NOT NULL,
  date TEXT NOT NULL,             -- upstream outage day; values are imputed
  PRIMARY KEY (ecosystem, date)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS hf_models (
  id TEXT PRIMARY KEY,            -- org/name
  org TEXT NOT NULL,
  task TEXT,
  library TEXT,
  created_at TEXT,
  first_seen TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS hf_model_daily (
  id TEXT NOT NULL,
  date TEXT NOT NULL,
  downloads_30d REAL NOT NULL,    -- Hub's trailing-30-day download count
  likes REAL NOT NULL,
  trending REAL,
  PRIMARY KEY (id, date)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS hf_agg_daily (
  dim   TEXT NOT NULL,            -- org | task
  key   TEXT NOT NULL,
  date  TEXT NOT NULL,
  downloads_30d REAL NOT NULL,
  models INTEGER NOT NULL,
  likes REAL NOT NULL,
  PRIMARY KEY (dim, key, date)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  ok INTEGER,
  summary TEXT
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

CREATE INDEX IF NOT EXISTS idx_metrics_metric_date ON metrics(metric, date);
CREATE INDEX IF NOT EXISTS idx_hf_daily_date ON hf_model_daily(date);
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
