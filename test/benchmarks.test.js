import test from 'node:test';
import assert from 'node:assert/strict';
import { K_MIN, anonymize, applyFilters, findCohort, groupBy, percentile, percentileRank, screen, summarize } from '../server/benchmarks.js';
import { followerBucket, parseDeal } from '../server/domain.js';

const deal = (o = {}) => ({ sport: 'football', level: 'power4', deal_type: 'social_post', payer_type: 'local_business', followers: 3000, total_usd: 500, in_kind_usd: 0, clearance: 'cleared', signed_quarter: '2026-Q3', verified: 0, ...o });
const many = (n, o, f = (i) => 100 * (i + 1)) => Array.from({ length: n }, (_, i) => deal({ ...o, total_usd: f(i) }));

test('percentile interpolates', () => {
  assert.equal(percentile([10, 20, 30, 40], 0.5), 25);
  assert.equal(percentile([10, 20, 30], 0), 10);
  assert.equal(percentile([], 0.5), null);
});

test('cohorts below the floor are suppressed, with no statistics at all', () => {
  assert.deepEqual(summarize(many(K_MIN - 1)), { n: K_MIN - 1, suppressed: true });
  const ok = summarize(many(K_MIN));
  assert.equal(ok.median, 300);
  assert.equal(ok.suppressed, false);
});

test('cleared rate only counts decided deals and needs enough of them', () => {
  const rows = [...many(6, { clearance: 'cleared' }), ...many(2, { clearance: 'not_cleared' }), ...many(5, { clearance: 'not_submitted' })];
  assert.equal(summarize(rows).cleared_rate, 0.75);
  assert.equal(summarize(many(6, { clearance: 'pending' })).cleared_rate, null);
});

test('groupBy drops suppressed groups and orders follower buckets naturally', () => {
  const rows = [...many(6, { followers: 200_000 }), ...many(7, { followers: 500 }), ...many(2, { followers: 20_000 })];
  assert.deepEqual(groupBy(rows, 'followers').map((r) => r.key), ['under_1k', '100k_500k']);
  assert.equal(followerBucket(999), 'under_1k');
  assert.equal(followerBucket(1000), '1k_5k');
  assert.equal(followerBucket(9_000_000), '500k_plus');
});

test('findCohort uses an exact match when it is big enough', () => {
  const found = findCohort([...many(15), ...many(30, { sport: 'baseball' })], deal());
  assert.equal(found.cohort.length, 15);
  assert.deepEqual(found.widened, []);
});

test('findCohort widens step by step and says what it relaxed', () => {
  const pool = [...many(3), ...many(12, { payer_type: 'national_brand' }), ...many(40, { sport: 'golf' })];
  const found = findCohort(pool, deal());
  assert.equal(found.cohort.length, 15);
  assert.deepEqual(found.widened, ['any payer type']);
  assert.ok(found.cohort.every((d) => d.sport === 'football'));
});

test('findCohort returns nothing rather than a cohort below the floor', () => {
  assert.equal(findCohort(many(3), deal()).cohort.length, 0);
});

test('percentile rank and filters', () => {
  const pool = many(10);
  assert.equal(percentileRank(pool, 500), 0.5);
  assert.equal(percentileRank(pool, 50), 0);
  assert.equal(applyFilters(pool, { sport: 'football', level: '', followers: ['1k_5k', '5k_10k'] }).length, 10);
  assert.equal(applyFilters(pool, { sport: 'golf' }).length, 0);
});

test('anonymize rounds money and buckets followers; no exact figures leave', () => {
  const out = anonymize(deal({ total_usd: 12345, followers: 48211, in_kind_usd: 5 }));
  assert.equal(out.total_usd, 12000);
  assert.equal(out.followers, '10k_50k');
  assert.equal(out.in_kind, true);
  assert.ok(!('cash_usd' in out) && !('user_id' in out) && !('id' in out) && !('region' in out));
});

test('screening flags implausible submissions', () => {
  assert.deepEqual(screen(deal(), []), []);
  assert.ok(screen(deal({ total_usd: 300_000 }), []).length);
  assert.ok(screen(deal({ total_usd: 60_000, followers: 100 }), []).length);
  assert.ok(screen(deal({ total_usd: 900, clearance: 'not_required' }), []).length);
  assert.ok(screen(deal({ total_usd: 90_000, followers: 80_000 }), many(25)).some((f) => f.includes('40×')));
});

test('parseDeal validates every field and requires both attestations', () => {
  const good = { sport: 'softball', level: 'd1', class_year: 'jr', region: 'midwest', followers: 4200, payer_type: 'local_business', industry: 'food_beverage', deal_type: 'social_post', cash_usd: 250, in_kind_usd: 50, clearance: 'not_required', signed_quarter: '2026-Q2', attest_adult: true, attest_right: true };
  const now = new Date('2026-11-27');
  const parsed = parseDeal(good, now);
  assert.equal(parsed.total_usd, 300);
  assert.equal(parsed.deliverables, 1);
  const bad = (o, field) => assert.throws(() => parseDeal({ ...good, ...o }, now), (e) => field in e.fields);
  bad({ sport: 'quidditch' }, 'sport');
  bad({ cash_usd: 0, in_kind_usd: 0 }, 'cash_usd');
  bad({ cash_usd: -5 }, 'cash_usd');
  bad({ followers: 1.5 }, 'followers');
  bad({ signed_quarter: '2027-Q1' }, 'signed_quarter');
  bad({ signed_quarter: '2020-Q1' }, 'signed_quarter');
  bad({ attest_adult: false }, 'attest_adult');
  bad({ attest_right: undefined }, 'attest_right');
});
