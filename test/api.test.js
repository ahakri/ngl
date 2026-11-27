import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import { addDays, openDb, today } from '../server/db.js';
import { config } from '../server/config.js';
import { buildApp } from '../server/app.js';
import { recomputeSignals, saveHfSnapshot, upsertMetric } from '../server/store.js';
import { applyEvent, verifyWebhook } from '../server/billing.js';
import { hashPassword, verifyPassword } from '../server/auth.js';

function seeded() {
  const db = openDb(':memory:');
  const end = addDays(today(), -1);
  const pts = (fn) => Array.from({ length: 150 }, (_, i) => ({ date: addDays(end, -i), value: fn(i) }));
  upsertMetric(db, 'openai', 'pypi_downloads', pts(() => 10000));
  upsertMetric(db, 'anthropic', 'pypi_downloads', pts((i) => (i < 28 ? 3000 : 1000)));
  upsertMetric(db, 'mistralai', 'pypi_downloads', pts(() => 100));
  upsertMetric(db, 'openai', 'npm_downloads', pts(() => 500));
  recomputeSignals(db);
  saveHfSnapshot(db, today(), [
    { id: 'acme/big', org: 'acme', task: 'text-generation', library: 'transformers', createdAt: null, downloads: 900, likes: 10, trending: 5 },
    { id: 'other/small', org: 'other', task: 'text-generation', library: null, createdAt: null, downloads: 100, likes: 1, trending: 9 },
  ]);
  return db;
}

const json = { 'content-type': 'application/json' };

test('data API: leaderboard, share, movers and plan gating', async () => {
  const db = seeded();
  const app = buildApp(db);

  const cat = (await app.inject('/v1/categories/model-sdks?ecosystem=pypi')).json();
  assert.equal(cat.plan, 'free');
  assert.deepEqual(cat.leaderboard.map((r) => r.project), ['openai', 'anthropic', 'mistralai']);
  assert.equal(cat.leaderboard[1].growth_28d, 2);
  assert.ok(cat.share.dates.length > 0 && cat.share.dates.length <= 12, 'free plan caps share history');

  const movers = (await app.inject('/v1/movers?ecosystem=pypi&limit=50')).json();
  assert.equal(movers.limit_cap, 5);
  assert.equal(movers.data[0].project, 'anthropic');
  assert.ok(!movers.data.some((r) => r.project === 'mistralai'), 'low-volume projects are excluded from movers');

  const proj = (await app.inject('/v1/projects/openai?days=9999')).json();
  assert.equal(proj.history_days, 90);
  assert.equal(proj.series.pypi.length, 90);
  assert.deepEqual(Object.keys(proj.series).sort(), ['npm', 'pypi']);

  assert.equal((await app.inject('/v1/projects/nope')).statusCode, 404);
  assert.equal((await app.inject('/v1/movers?ecosystem=cargo')).statusCode, 400);
  assert.equal((await app.inject('/v1/export/signals.csv')).statusCode, 402);

  const orgs = (await app.inject('/v1/models/orgs')).json();
  assert.equal(orgs.rows[0].org, 'acme');
  assert.equal(orgs.rows[0].share, 0.9);
  const trending = (await app.inject('/v1/models?sort=trending')).json();
  assert.equal(trending.rows[0].id, 'other/small');
  await app.close();
});

test('accounts: signup, session, API keys, metering, quota and export', async () => {
  const db = seeded();
  const app = buildApp(db);

  const bad = await app.inject({ method: 'POST', url: '/api/auth/signup', headers: json, payload: { email: 'a@b.co', password: 'short' } });
  assert.equal(bad.statusCode, 400);

  const signup = await app.inject({ method: 'POST', url: '/api/auth/signup', headers: json, payload: { email: 'Analyst@Fund.com', password: 'correct horse battery' } });
  assert.equal(signup.statusCode, 200);
  const cookie = signup.cookies.find((c) => c.name === 'uptake_session');
  assert.ok(cookie.httpOnly);
  const cookies = { uptake_session: cookie.value };

  assert.equal((await app.inject({ method: 'POST', url: '/api/auth/signup', headers: json, payload: { email: 'analyst@fund.com', password: 'correct horse battery' } })).statusCode, 409);
  assert.equal((await app.inject({ method: 'POST', url: '/api/auth/login', headers: json, payload: { email: 'analyst@fund.com', password: 'wrong password!' } })).statusCode, 401);
  assert.equal((await app.inject({ method: 'POST', url: '/api/keys', headers: json, payload: {} })).statusCode, 401);
  // Form posts (the cross-site CSRF vector) are refused outright.
  assert.equal((await app.inject({ method: 'POST', url: '/api/keys', cookies, headers: { 'content-type': 'application/x-www-form-urlencoded' }, payload: 'name=x' })).statusCode, 415);

  const created = (await app.inject({ method: 'POST', url: '/api/keys', cookies, headers: json, payload: { name: 'notebook' } })).json().key;
  assert.match(created.key, /^upk_/);
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM api_keys WHERE key_hash = ?').get(created.key).n, 0, 'key is stored hashed');

  const bearer = { authorization: `Bearer ${created.key}` };
  const first = await app.inject({ url: '/v1/meta', headers: bearer });
  assert.equal(first.statusCode, 200);
  assert.equal(first.headers['x-ratelimit-remaining'], '99');

  // Exhaust the free quota.
  db.prepare('UPDATE usage SET requests = 100').run();
  const over = await app.inject({ url: '/v1/meta', headers: bearer });
  assert.equal(over.statusCode, 429);
  assert.equal(over.json().error.code, 'quota_exceeded');

  // Upgrade → quota and export open up.
  db.prepare("UPDATE users SET plan = 'pro'").run();
  const csv = await app.inject({ url: '/v1/export/signals.csv?ecosystem=pypi', headers: bearer });
  assert.equal(csv.statusCode, 200);
  assert.match(csv.body.split('\n')[0], /^project,name,vendor/);
  assert.equal(csv.body.trim().split('\n').length, 4);
  const full = (await app.inject({ url: '/v1/projects/openai?days=9999', headers: bearer })).json();
  assert.equal(full.series.pypi.length, 150);

  const me = (await app.inject({ url: '/api/me', cookies })).json();
  assert.equal(me.user.email, 'analyst@fund.com');
  assert.equal(me.keys.length, 1);
  assert.ok(me.usage[0].requests > 100);

  assert.equal((await app.inject({ method: 'DELETE', url: `/api/keys/${created.id}`, cookies })).statusCode, 200);
  assert.equal((await app.inject({ url: '/v1/meta', headers: bearer })).statusCode, 401);

  // Password change: needs the current password, and signs out other sessions.
  const other = (await app.inject({ method: 'POST', url: '/api/auth/login', headers: json, payload: { email: 'analyst@fund.com', password: 'correct horse battery' } })).cookies[0].value;
  assert.equal((await app.inject({ method: 'POST', url: '/api/auth/password', cookies, headers: json, payload: { current: 'nope', next: 'a brand new password' } })).statusCode, 401);
  assert.equal((await app.inject({ method: 'POST', url: '/api/auth/password', cookies, headers: json, payload: { current: 'correct horse battery', next: 'a brand new password' } })).statusCode, 200);
  assert.equal((await app.inject({ url: '/api/me', cookies: { uptake_session: other } })).json().user, null);
  assert.equal((await app.inject({ url: '/api/me', cookies })).json().user.email, 'analyst@fund.com');
  assert.equal((await app.inject({ method: 'POST', url: '/api/auth/login', headers: json, payload: { email: 'analyst@fund.com', password: 'a brand new password' } })).statusCode, 200);

  await app.inject({ method: 'POST', url: '/api/auth/logout', cookies, headers: json, payload: {} });
  assert.equal((await app.inject({ url: '/api/me', cookies })).json().user, null);
  await app.close();
});

test('passwords: scrypt round trip', () => {
  const h = hashPassword('correct horse battery');
  assert.ok(verifyPassword('correct horse battery', h));
  assert.ok(!verifyPassword('correct horse batterx', h));
  assert.ok(!verifyPassword('x', 'garbage'));
});

test('stripe: signature verification and subscription lifecycle', async () => {
  const secret = 'whsec_test';
  const sign = (body, t = Math.floor(Date.now() / 1000)) => `t=${t},v1=${crypto.createHmac('sha256', secret).update(`${t}.${body}`).digest('hex')}`;
  const body = JSON.stringify({ id: 'evt_1', type: 'checkout.session.completed', data: { object: { mode: 'subscription', client_reference_id: '1', customer: 'cus_1', subscription: 'sub_1', metadata: { plan: 'pro' } } } });

  assert.equal(verifyWebhook(body, sign(body), secret).id, 'evt_1');
  assert.throws(() => verifyWebhook(body + ' ', sign(body), secret), /mismatch/);
  assert.throws(() => verifyWebhook(body, sign(body, 1000), secret), /tolerance/);
  assert.throws(() => verifyWebhook(body, 'nonsense', secret), /Malformed/);

  const db = seeded();
  const app = buildApp(db);
  await app.inject({ method: 'POST', url: '/api/auth/signup', headers: json, payload: { email: 'pay@fund.com', password: 'correct horse battery' } });
  const plan = () => db.prepare('SELECT plan FROM users WHERE id = 1').get().plan;

  config.stripe.webhookSecret = secret;
  config.stripe.prices.pro = 'price_pro';
  const forged = await app.inject({ method: 'POST', url: '/api/billing/webhook', headers: { ...json, 'stripe-signature': sign('{}') }, payload: body });
  assert.equal(forged.statusCode, 400);
  assert.equal(plan(), 'free');

  const ok = await app.inject({ method: 'POST', url: '/api/billing/webhook', headers: { ...json, 'stripe-signature': sign(body) }, payload: body });
  assert.equal(ok.json().result, 'upgraded');
  assert.equal(plan(), 'pro');
  assert.equal(applyEvent(db, JSON.parse(body)), 'duplicate');

  assert.equal(applyEvent(db, { id: 'evt_2', type: 'customer.subscription.deleted', data: { object: { id: 'sub_1', customer: 'cus_1', status: 'canceled' } } }), 'plan:free');
  assert.equal(plan(), 'free');
  config.stripe.webhookSecret = '';
  config.stripe.prices.pro = '';
  await app.close();
});
