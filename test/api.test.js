import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import { openDb } from '../server/db.js';
import { config } from '../server/config.js';
import { buildApp } from '../server/app.js';
import { seedDemo } from '../server/demo.js';
import { applyEvent, verifyWebhook } from '../server/billing.js';
import { hashPassword, verifyPassword } from '../server/auth.js';
import { quarterOf } from '../server/domain.js';

const json = { 'content-type': 'application/json' };
const DEAL = { sport: 'softball', level: 'd1', class_year: 'jr', region: 'midwest', followers: 4200, payer_type: 'local_business', industry: 'food_beverage', deal_type: 'social_post', cash_usd: 250, in_kind_usd: 50, clearance: 'not_required', signed_quarter: quarterOf(), attest_adult: true, attest_right: true };

async function setup(seed = 600) {
  const db = openDb(':memory:');
  if (seed) seedDemo(db, seed);
  const app = buildApp(db);
  const signup = async (email) => {
    const res = await app.inject({ method: 'POST', url: '/api/auth/signup', headers: json, payload: { email, password: 'correct horse battery' } });
    return { rf_session: res.cookies.find((c) => c.name === 'rf_session').value };
  };
  return { db, app, signup };
}
const post = (app, url, cookies, payload) => app.inject({ method: 'POST', url, cookies, headers: json, payload });

test('visitors see only the public summary', async () => {
  const { app } = await setup();
  const summary = (await app.inject('/v1/summary')).json();
  assert.equal(summary.dataset.deals, 600);
  assert.equal(summary.dataset.demo_data, true);
  assert.ok(summary.by_sport.length > 3);
  assert.deepEqual(Object.keys(summary.by_sport[0]).sort(), ['key', 'label', 'median', 'n'], 'no percentile bands in the teaser');
  assert.equal((await app.inject('/v1/benchmarks')).statusCode, 402);
  assert.equal((await app.inject('/v1/comps')).statusCode, 402);
  assert.equal((await post(app, '/v1/rangefinder', undefined, {})).statusCode, 402);
  assert.equal((await app.inject('/v1/meta')).json().tier, 'free');
  await app.close();
});

test('give to get: sharing a deal unlocks the explorer and range finder', async () => {
  const { app, signup, db } = await setup();
  const cookies = await signup('athlete@example.edu');
  assert.equal((await app.inject({ url: '/v1/benchmarks', cookies })).statusCode, 402);

  const bad = await post(app, '/api/deals', cookies, { ...DEAL, attest_adult: false, sport: 'nope' });
  assert.equal(bad.statusCode, 400);
  assert.deepEqual(Object.keys(bad.json().error.fields).sort(), ['attest_adult', 'sport']);
  assert.equal((await post(app, '/api/deals', undefined, DEAL)).statusCode, 401);

  const sub = await post(app, '/api/deals', cookies, DEAL);
  assert.equal(sub.json().deal.status, 'approved');
  assert.equal((await post(app, '/api/deals', cookies, DEAL)).statusCode, 409, 'duplicate refused');

  const me = (await app.inject({ url: '/api/me', cookies })).json();
  assert.equal(me.tier, 'contributor');
  assert.equal(me.deals.length, 1);

  const bench = (await app.inject({ url: '/v1/benchmarks?group_by=level&sport=football', cookies })).json();
  assert.ok(bench.overall.median > 0);
  assert.ok(bench.rows.every((r) => r.n >= bench.k_min && r.p25 <= r.median && r.median <= r.p75));
  assert.equal((await app.inject({ url: '/v1/benchmarks?sport=quidditch', cookies })).statusCode, 400);

  const rf = (await post(app, '/v1/rangefinder', cookies, { sport: 'football', level: 'power4', deal_type: 'social_post', payer_type: 'local_business', followers: 3000, amount: 1_000_000 })).json();
  assert.ok(rf.basis.n >= 5);
  assert.equal(rf.position, 'well_above');
  assert.equal(rf.percentile, 1);
  assert.ok(rf.comps.length > 0 && rf.comps.length <= 8);
  assert.ok(!('id' in rf.comps[0]) && !('cash_usd' in rf.comps[0]));
  assert.equal((await app.inject({ url: '/v1/export/benchmarks.csv', cookies })).statusCode, 402);

  // Withdrawing the only deal ends contributor access.
  assert.equal((await app.inject({ method: 'DELETE', url: `/api/deals/${sub.json().deal.id}`, cookies })).statusCode, 200);
  assert.equal((await app.inject({ url: '/v1/benchmarks', cookies })).statusCode, 402);
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM deals WHERE is_demo = 0').get().n, 0);
  await app.close();
});

test('thin cohorts are never listed', async () => {
  const { app, signup } = await setup(0);
  const cookies = await signup('first@example.edu');
  await post(app, '/api/deals', cookies, DEAL);
  const bench = (await app.inject({ url: '/v1/benchmarks', cookies })).json();
  assert.deepEqual(bench.overall, { n: 1, suppressed: true });
  assert.deepEqual(bench.rows, []);
  assert.deepEqual((await app.inject({ url: '/v1/comps', cookies })).json().rows, []);
  const rf = (await post(app, '/v1/rangefinder', cookies, { ...DEAL, amount: 300 })).json();
  assert.equal(rf.stats.suppressed, true);
  assert.deepEqual(rf.comps, []);
  assert.equal((await app.inject('/v1/summary')).json().overall.suppressed, true);
  await app.close();
});

test('moderation: flagged deals wait, only admins review, rejection ends access', async () => {
  const { app, signup } = await setup();
  const athlete = await signup('big@example.edu');
  const admin = await signup('mod@example.com');
  config.adminEmails = ['mod@example.com'];

  const sub = (await post(app, '/api/deals', athlete, { ...DEAL, cash_usd: 400_000, clearance: 'cleared' })).json().deal;
  assert.equal(sub.status, 'pending');
  assert.ok(sub.flags.length);
  assert.equal((await app.inject('/v1/summary')).json().dataset.deals, 600, 'pending deals are not published');
  assert.equal((await app.inject({ url: '/api/me', cookies: athlete })).json().tier, 'contributor', 'access while under review');

  assert.equal((await app.inject({ url: '/api/admin/queue', cookies: athlete })).statusCode, 403);
  const queue = (await app.inject({ url: '/api/admin/queue', cookies: admin })).json().deals;
  assert.equal(queue.length, 1);
  assert.equal(queue[0].user_id, undefined);

  await post(app, `/api/admin/deals/${sub.id}`, admin, { action: 'reject' });
  assert.equal((await app.inject({ url: '/api/me', cookies: athlete })).json().tier, 'free');

  const second = (await post(app, '/api/deals', athlete, { ...DEAL, cash_usd: 300_000, clearance: 'cleared' })).json().deal;
  await post(app, `/api/admin/deals/${second.id}`, admin, { action: 'verify' });
  const stats = (await app.inject('/v1/summary')).json().dataset;
  assert.equal(stats.deals, 601);
  assert.equal(stats.verified, 1);
  config.adminEmails = [];
  await app.close();
});

test('paid plans, API keys, quota and export', async () => {
  const { app, signup, db } = await setup();
  const cookies = await signup('agent@agency.com');
  const key = (await post(app, '/api/keys', cookies, { name: 'crm' })).json().key;
  assert.match(key.key, /^rfk_/);
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM api_keys WHERE key_hash = ?').get(key.key).n, 0, 'key is stored hashed');
  const bearer = { authorization: `Bearer ${key.key}` };

  assert.equal((await app.inject({ url: '/v1/benchmarks', headers: bearer })).statusCode, 402);
  db.prepare("UPDATE users SET plan = 'pro'").run();
  const ok = await app.inject({ url: '/v1/benchmarks?group_by=quarter', headers: bearer });
  assert.equal(ok.statusCode, 200);
  assert.equal(ok.headers['x-rangefinder-tier'], 'pro');
  const quarters = ok.json().rows.map((r) => r.key);
  assert.deepEqual(quarters, [...quarters].sort());

  const csv = await app.inject({ url: '/v1/export/benchmarks.csv?group_by=deal_type', headers: bearer });
  assert.match(csv.body.split('\n')[0], /^key,label,n,p10,p25,median/);
  assert.equal((await app.inject({ url: '/v1/comps?sport=football', headers: bearer })).json().limit_cap, 50);

  db.prepare('UPDATE usage SET requests = 5000').run();
  assert.equal((await app.inject({ url: '/v1/meta', headers: bearer })).json().error.code, 'quota_exceeded');
  assert.equal((await app.inject({ url: '/v1/meta', headers: { authorization: 'Bearer rfk_nope' } })).statusCode, 401);
  // Form posts (the cross-site CSRF vector) are refused outright.
  assert.equal((await app.inject({ method: 'POST', url: '/api/keys', cookies, headers: { 'content-type': 'application/x-www-form-urlencoded' }, payload: 'name=x' })).statusCode, 415);
  await app.close();
});

test('passwords: scrypt round trip and change', async () => {
  const h = hashPassword('correct horse battery');
  assert.ok(verifyPassword('correct horse battery', h));
  assert.ok(!verifyPassword('correct horse batterx', h));
  const { app, signup } = await setup(0);
  const cookies = await signup('pw@example.com');
  assert.equal((await post(app, '/api/auth/password', cookies, { current: 'nope', next: 'a brand new password' })).statusCode, 401);
  assert.equal((await post(app, '/api/auth/password', cookies, { current: 'correct horse battery', next: 'a brand new password' })).statusCode, 200);
  assert.equal((await post(app, '/api/auth/login', undefined, { email: 'pw@example.com', password: 'a brand new password' })).statusCode, 200);
  await app.close();
});

test('stripe: signature verification and subscription lifecycle', async () => {
  const secret = 'whsec_test';
  const sign = (body, t = Math.floor(Date.now() / 1000)) => `t=${t},v1=${crypto.createHmac('sha256', secret).update(`${t}.${body}`).digest('hex')}`;
  const body = JSON.stringify({ id: 'evt_1', type: 'checkout.session.completed', data: { object: { mode: 'subscription', client_reference_id: '1', customer: 'cus_1', subscription: 'sub_1', metadata: { plan: 'pro' } } } });
  assert.equal(verifyWebhook(body, sign(body), secret).id, 'evt_1');
  assert.throws(() => verifyWebhook(`${body} `, sign(body), secret), /mismatch/);
  assert.throws(() => verifyWebhook(body, sign(body, 1000), secret), /tolerance/);

  const { app, signup, db } = await setup(0);
  await signup('pay@agency.com');
  const plan = () => db.prepare('SELECT plan FROM users WHERE id = 1').get().plan;
  config.stripe.webhookSecret = secret;
  config.stripe.prices.pro = 'price_pro';
  const forged = await app.inject({ method: 'POST', url: '/api/billing/webhook', headers: { ...json, 'stripe-signature': sign('{}') }, payload: body });
  assert.equal(forged.statusCode, 400);
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
