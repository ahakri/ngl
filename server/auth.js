// Accounts, sessions and API keys. Secrets are never stored in the clear:
// passwords use scrypt; session tokens and API keys are stored as SHA-256.
import crypto from 'node:crypto';
import { today } from './db.js';

const SESSION_DAYS = 30;
export const SESSION_COOKIE = 'uptake_session';
const sha = (s) => crypto.createHash('sha256').update(s).digest('hex');
const now = () => new Date().toISOString();

export function hashPassword(password) {
  const salt = crypto.randomBytes(16);
  const hash = crypto.scryptSync(password, salt, 64, { N: 16384, r: 8, p: 1 });
  return `scrypt$${salt.toString('hex')}$${hash.toString('hex')}`;
}

export function verifyPassword(password, stored) {
  const [scheme, saltHex, hashHex] = String(stored).split('$');
  if (scheme !== 'scrypt' || !saltHex || !hashHex) return false;
  const expected = Buffer.from(hashHex, 'hex');
  const actual = crypto.scryptSync(password, Buffer.from(saltHex, 'hex'), expected.length, { N: 16384, r: 8, p: 1 });
  return crypto.timingSafeEqual(expected, actual);
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export class AuthError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.status = status;
  }
}

export function createUser(db, email, password) {
  email = String(email || '').trim().toLowerCase();
  if (!EMAIL_RE.test(email) || email.length > 254) throw new AuthError('Enter a valid email address.');
  if (typeof password !== 'string' || password.length < 10 || password.length > 200) throw new AuthError('Password must be at least 10 characters.');
  if (db.prepare('SELECT 1 FROM users WHERE email = ?').get(email)) throw new AuthError('An account with that email already exists.', 409);
  const id = db.prepare('INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)').run(email, hashPassword(password), now()).lastInsertRowid;
  return getUser(db, Number(id));
}

export function authenticate(db, email, password) {
  const row = db.prepare('SELECT * FROM users WHERE email = ?').get(String(email || '').trim().toLowerCase());
  // Hash even when the user is unknown so timing doesn't reveal which emails exist.
  const ok = verifyPassword(String(password || ''), row?.password_hash || hashPassword('x'.repeat(12)));
  if (!row || !ok) throw new AuthError('Incorrect email or password.', 401);
  return publicUser(row);
}

const publicUser = (r) => r && { id: r.id, email: r.email, plan: r.plan, created_at: r.created_at, has_subscription: Boolean(r.stripe_subscription_id) };
export const getUser = (db, id) => publicUser(db.prepare('SELECT * FROM users WHERE id = ?').get(id));

export function createSession(db, userId) {
  const token = crypto.randomBytes(32).toString('base64url');
  const expires = new Date(Date.now() + SESSION_DAYS * 86400e3);
  db.prepare('INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)').run(sha(token), userId, expires.toISOString());
  db.prepare('DELETE FROM sessions WHERE expires_at < ?').run(now());
  return { token, maxAge: SESSION_DAYS * 86400 };
}

export function userFromSession(db, token) {
  if (!token) return null;
  const row = db.prepare('SELECT user_id FROM sessions WHERE token_hash = ? AND expires_at > ?').get(sha(token), now());
  return row ? getUser(db, row.user_id) : null;
}

export const destroySession = (db, token) => token && db.prepare('DELETE FROM sessions WHERE token_hash = ?').run(sha(token));

const MAX_KEYS = 10;

export function createApiKey(db, userId, name) {
  name = String(name || '').trim().slice(0, 60) || 'default';
  const active = db.prepare('SELECT COUNT(*) AS n FROM api_keys WHERE user_id = ? AND revoked_at IS NULL').get(userId).n;
  if (active >= MAX_KEYS) throw new AuthError(`You can have at most ${MAX_KEYS} active keys. Revoke one first.`);
  const key = `upk_${crypto.randomBytes(30).toString('base64url')}`;
  const prefix = key.slice(0, 10);
  const id = db.prepare('INSERT INTO api_keys (user_id, name, prefix, key_hash, created_at) VALUES (?, ?, ?, ?, ?)').run(userId, name, prefix, sha(key), now()).lastInsertRowid;
  return { id: Number(id), name, prefix, key }; // the full key is returned exactly once
}

export const listApiKeys = (db, userId) =>
  db.prepare('SELECT id, name, prefix, created_at, last_used_at FROM api_keys WHERE user_id = ? AND revoked_at IS NULL ORDER BY id DESC').all(userId);

export const revokeApiKey = (db, userId, id) =>
  db.prepare('UPDATE api_keys SET revoked_at = ? WHERE id = ? AND user_id = ? AND revoked_at IS NULL').run(now(), id, userId).changes > 0;

export function userFromApiKey(db, key) {
  if (!key || !key.startsWith('upk_')) return null;
  const row = db.prepare('SELECT id, user_id FROM api_keys WHERE key_hash = ? AND revoked_at IS NULL').get(sha(key));
  if (!row) return null;
  db.prepare('UPDATE api_keys SET last_used_at = ? WHERE id = ?').run(now(), row.id);
  return getUser(db, row.user_id);
}

/** Count one metered request; returns the running total for today. */
export function meter(db, userId) {
  return db.prepare(`INSERT INTO usage (user_id, date, requests) VALUES (?, ?, 1)
    ON CONFLICT (user_id, date) DO UPDATE SET requests = requests + 1 RETURNING requests`).get(userId, today()).requests;
}

export const usageHistory = (db, userId, days = 30) =>
  db.prepare('SELECT date, requests FROM usage WHERE user_id = ? ORDER BY date DESC LIMIT ?').all(userId, days);

/** Fixed-window in-memory limiter for unauthenticated traffic. */
export function createLimiter(max, windowMs) {
  const hits = new Map();
  return (key) => {
    const t = Date.now();
    if (hits.size > 50000) for (const [k, v] of hits) if (v.reset < t) hits.delete(k);
    const cur = hits.get(key);
    if (!cur || cur.reset < t) {
      hits.set(key, { n: 1, reset: t + windowMs });
      return true;
    }
    return ++cur.n <= max;
  };
}
