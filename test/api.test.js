import test from 'node:test';
import assert from 'node:assert/strict';
import { addDays, openDb, today } from '../server/db.js';
import { buildApp } from '../server/app.js';
import { jurisdictionByClient } from '../server/jurisdictions.js';
import { reclassify, saveMatter } from '../server/store.js';

const json = { 'content-type': 'application/json' };
const matter = (id, title, date, o = {}) => ({ external_id: String(id), title, intro_date: date, agenda_date: date, status_name: 'Agenda Ready', url: `https://example.test/${id}`, ...o });

async function setup() {
  const db = openDb(':memory:');
  const mesa = jurisdictionByClient.get('mesa');
  const hayward = jurisdictionByClient.get('hayward');
  const old = addDays(today(), -200);
  const fresh = addDays(today(), -3);
  const future = addDays(today(), 10);
  saveMatter(db, mesa, matter(1, 'ZON1-0001. "Alpha Campus" 120± acres. Rezone to allow for a 900,000 square foot Data Center development.', old, { status_name: 'Passed' }), [{ external_id: 'h1', date: old, action: 'Approved', result: 'Pass', body: 'City Council', tally: '7-0' }]);
  saveMatter(db, mesa, matter(2, 'ZON1-0002. "Beta Campus" 60 acres. Site Plan for a Data Center development.', fresh));
  saveMatter(db, mesa, matter(3, 'ZON1-0003. "Gamma Campus" 40 acres. Use Permit for a Data Center development.', future));
  saveMatter(db, hayward, matter(4, 'Extension of Moratorium on New Data Centers', old));
  saveMatter(db, hayward, matter(5, 'Purchase orders for servers in the City data center for the Department of Technology', old));
  const app = buildApp(db);
  const signup = async (email) => ({ sl_session: (await app.inject({ method: 'POST', url: '/api/auth/signup', headers: json, payload: { email, password: 'correct horse battery' } })).cookies.find((c) => c.name === 'sl_session').value });
  return { db, app, signup };
}
const post = (app, url, cookies, payload) => app.inject({ method: 'POST', url, cookies, headers: json, payload });

test('free tier: delayed records, no calendar, no export; government IT never appears', async () => {
  const { app } = await setup();
  const list = (await app.inject('/v1/records')).json();
  assert.equal(list.embargo_days, 30);
  assert.deepEqual(list.data.map((r) => r.id).sort(), [1, 4]);
  assert.equal(list.withheld_by_plan, 2);
  assert.equal(list.data.find((r) => r.id === 1).acres, 120);
  assert.equal(list.data.find((r) => r.id === 4).restrictive, true);

  assert.equal((await app.inject('/v1/records/2')).statusCode, 402, 'recent record is embargoed');
  assert.equal((await app.inject('/v1/records/5')).statusCode, 404, 'excluded category is not addressable');
  const detail = (await app.inject('/v1/records/1')).json();
  assert.equal(detail.outcome, 'approved');
  assert.equal(detail.actions[0].tally, '7-0');
  assert.equal((await app.inject('/v1/upcoming')).statusCode, 402);
  assert.equal((await app.inject('/v1/export/records.csv')).statusCode, 402);

  const s = (await app.inject('/v1/summary')).json();
  assert.equal(s.totals.records, 4);
  assert.equal(s.totals.upcoming_hearings, 1);
  assert.equal(s.totals.restrictive_last_12_months, 1);
  await app.close();
});

test('filters validate and narrow', async () => {
  const { app } = await setup();
  assert.equal((await app.inject('/v1/records?state=ZZ')).statusCode, 400);
  assert.equal((await app.inject('/v1/records?category=municipal_it')).statusCode, 400);
  assert.equal((await app.inject('/v1/records?since=yesterday')).statusCode, 400);
  assert.deepEqual((await app.inject('/v1/records?state=ca')).json().data.map((r) => r.id), [4]);
  assert.deepEqual((await app.inject('/v1/records?restrictive=1')).json().data.map((r) => r.id), [4]);
  assert.deepEqual((await app.inject('/v1/records?q=alpha')).json().data.map((r) => r.id), [1]);
  assert.equal((await app.inject('/v1/records?q=%25')).json().total, 0, 'wildcards in search are literal');
  await app.close();
});

test('pro tier: live records, calendar, export, watches and private feeds', async () => {
  const { app, signup, db } = await setup();
  const cookies = await signup('dev@example.com');
  assert.equal((await post(app, '/api/watches', cookies, { name: 'AZ projects', filters: { state: 'AZ' } })).statusCode, 402);
  db.prepare("UPDATE users SET plan = 'pro'").run();

  const list = (await app.inject({ url: '/v1/records', cookies })).json();
  assert.equal(list.total, 4);
  assert.equal(list.withheld_by_plan, 0);
  assert.deepEqual((await app.inject({ url: '/v1/upcoming', cookies })).json().data.map((r) => r.id), [3]);
  const csv = await app.inject({ url: '/v1/export/records.csv?state=AZ', cookies });
  assert.match(csv.body.split('\n')[0], /^id,event_date,state,jurisdiction,category/);
  assert.equal(csv.body.trim().split('\n').length, 4);

  assert.equal((await post(app, '/api/watches', cookies, { name: 'bad', filters: { state: 'ZZ' } })).statusCode, 400);
  const watch = (await post(app, '/api/watches', cookies, { name: 'AZ <projects>', filters: { state: 'AZ', category: 'project' } })).json().watch;
  const path = new URL(watch.feed_url).pathname;
  const feed = await app.inject(path);
  assert.equal(feed.statusCode, 200);
  assert.match(feed.headers['content-type'], /atom\+xml/);
  assert.equal((feed.body.match(/<entry>/g) || []).length, 3);
  assert.ok(feed.body.includes('AZ &lt;projects&gt;') && !feed.body.includes('<projects>'), 'feed escapes user text');
  assert.equal((await app.inject('/feeds/not-a-token')).statusCode, 404);

  // Downgrade: the feed stops working.
  db.prepare("UPDATE users SET plan = 'free'").run();
  assert.equal((await app.inject(path)).statusCode, 402);
  const me = (await app.inject({ url: '/api/me', cookies })).json();
  assert.equal(me.watches.length, 1);
  assert.equal(me.watches[0].feed_token, undefined);
  assert.equal((await app.inject({ method: 'DELETE', url: `/api/watches/${watch.id}`, cookies })).statusCode, 200);
  await app.close();
});

test('API keys are metered; re-collecting updates in place', async () => {
  const { app, signup, db } = await setup();
  const cookies = await signup('k@example.com');
  const key = (await post(app, '/api/keys', cookies, { name: 'crm' })).json().key.key;
  assert.match(key, /^slk_/);
  const res = await app.inject({ url: '/v1/records', headers: { authorization: `Bearer ${key}` } });
  assert.equal(res.headers['x-ratelimit-remaining'], '99');
  db.prepare('UPDATE usage SET requests = 100').run();
  assert.equal((await app.inject({ url: '/v1/meta', headers: { authorization: `Bearer ${key}` } })).statusCode, 429);

  const mesa = jurisdictionByClient.get('mesa');
  const wasNew = saveMatter(db, mesa, matter(1, 'ZON1-0001. "Alpha Campus" 120± acres. Rezone for a Data Center development.', addDays(today(), -200), { status_name: 'Failed' }));
  assert.equal(wasNew, false);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM records WHERE jurisdiction = 'mesa'").get().n, 3);
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM actions WHERE record_id = 1').get().n, 1, 'history is kept');
  assert.equal(reclassify(db), 5);
  await app.close();
});

test('weekly digest: public headlines, sections, markdown and sign-up', async () => {
  const { app, db } = await setup();
  const d = (await app.inject('/v1/digest')).json();
  assert.equal(d.counts.records, 1, 'only the item from the last seven days');
  assert.equal(d.counts.upcoming, 1);
  assert.deepEqual(d.sections.map((s) => s.key), ['projects', 'upcoming']);
  assert.equal(d.sections[0].items[0].headline, 'Beta Campus');
  assert.ok(!('title' in d.sections[0].items[0]), 'headlines only, not full records');
  assert.match(d.markdown, /^# Data-centre siting: week of /);
  assert.match(d.markdown, /\*\*Mesa, AZ\*\*/);
  const quiet = (await app.inject('/v1/digest?week_ending=2001-01-07')).json();
  assert.equal(quiet.counts.records, 0);
  assert.match(quiet.markdown, /No new data-centre items/);

  assert.equal((await post(app, '/api/subscribe', undefined, { email: 'nope' })).statusCode, 400);
  assert.equal((await post(app, '/api/subscribe', undefined, { email: 'Reader@Example.com' })).statusCode, 200);
  assert.equal((await post(app, '/api/subscribe', undefined, { email: 'reader@example.com' })).statusCode, 200);
  assert.equal(db.prepare('SELECT COUNT(*) AS n FROM subscribers').get().n, 1);
  await app.close();
});
