import test from 'node:test';
import assert from 'node:assert/strict';
import { addDays } from '../server/db.js';
import { computeCategorySignals, detectBreaks, detectGaps, fillGaps, momentumScore, pickAsOf, shareSeries, windowSum } from '../server/pipeline/signals.js';

const END = '2026-06-30';
/** Daily series ending at END; fn(i) gives the value i days before END. */
const series = (days, fn) => new Map(Array.from({ length: days }, (_, i) => [addDays(END, -i), fn(i)]));

test('windowSum treats missing days as zero', () => {
  const s = new Map([[END, 5], [addDays(END, -2), 7]]);
  assert.equal(windowSum(s, END, 3), 12);
});

test('growth, share and rank for a simple two-horse category', () => {
  const flat = series(120, () => 100);
  const doubling = series(120, (i) => (i < 28 ? 200 : 100)); // doubled in the latest 28 days
  const rows = computeCategorySignals([{ slug: 'flat', series: flat }, { slug: 'up', series: doubling }], END);
  const up = rows.find((r) => r.project === 'up');
  const fl = rows.find((r) => r.project === 'flat');
  assert.equal(up.rank, 1);
  assert.equal(up.growth_28d, 1);
  assert.equal(fl.growth_28d, 0);
  assert.ok(Math.abs(up.share - 2 / 3) < 1e-9);
  assert.ok(Math.abs(up.share_delta_28d - (2 / 3 - 1 / 2)) < 1e-9);
  assert.equal(up.breakout, 0, 'below the minimum volume, never a breakout');
  assert.ok(up.momentum > 90 && fl.momentum < 50);
});

test('breakout needs growth, acceleration, share gain and volume', () => {
  const big = series(120, (i) => (i < 28 ? 2000 : 1000));
  const rival = series(120, () => 1000);
  const [top] = computeCategorySignals([{ slug: 'big', series: big }, { slug: 'rival', series: rival }], END);
  assert.equal(top.project, 'big');
  assert.equal(top.breakout, 1);
});

test('growth is null when history does not cover the base window', () => {
  const young = series(40, () => 50);
  const [row] = computeCategorySignals([{ slug: 'young', series: young }], END);
  assert.equal(row.growth_28d, null);
  assert.equal(row.momentum, null);
  assert.equal(row.growth_7d, 0);
});

test('growth is never computed across a structural break', () => {
  const s = series(120, (i) => (i < 40 ? 50 : 100)); // counting change 40 days ago halves the level
  const [naive] = computeCategorySignals([{ slug: 'x', series: s }], END);
  assert.ok(naive.growth_28d < -0.2, 'without the break the drop looks like real decline');
  const [aware] = computeCategorySignals([{ slug: 'x', series: s }], END, addDays(END, -39));
  assert.equal(aware.growth_28d, null);
  assert.equal(aware.growth_7d, 0);
});

test('detectBreaks finds a level shift and reports the first day of the new regime', () => {
  const weekday = (i) => ([0, 6].includes(new Date(`${addDays(END, -i)}T00:00:00Z`).getUTCDay()) ? 0.7 : 1);
  const s = series(150, (i) => (i <= 60 ? 480 : 1000) * weekday(i));
  const breaks = detectBreaks(s);
  assert.deepEqual(breaks.map((b) => b.date), [addDays(END, -60)]);
  assert.ok(Math.abs(breaks[0].ratio - 0.48) < 0.02);
});

test('detectBreaks ignores steady growth and a holiday dip', () => {
  const growing = series(200, (i) => 1000 * 1.004 ** (200 - i)); // ~12% a month
  assert.deepEqual(detectBreaks(growing), []);
  const holiday = series(200, (i) => (i >= 90 && i < 104 ? 500 : 1000)); // two quiet weeks, then back
  assert.deepEqual(detectBreaks(holiday), []);
});

test('gap days are detected on the aggregate and imputed from the same weekday', () => {
  const s = series(60, () => 100);
  const outage = addDays(END, -20);
  s.set(outage, 0);
  const gaps = detectGaps(s);
  assert.deepEqual([...gaps], [outage]);
  const filled = fillGaps(s, gaps);
  assert.equal(filled.get(outage), 100);
  assert.equal(s.get(outage), 0, 'raw series is not mutated');
});

test('pickAsOf skips a day most series have not reported yet', () => {
  const a = series(30, () => 1);
  const b = series(30, () => 1);
  const c = series(30, () => 1);
  b.delete(END);
  c.delete(END);
  assert.equal(pickAsOf([a, b, c]), addDays(END, -1));
});

test('momentum is bounded, 50 when flat', () => {
  assert.equal(momentumScore({ growth28: 0, growth7: 0, accel: 0, shareDelta: 0 }), 50);
  assert.ok(momentumScore({ growth28: 50, growth7: 9, accel: 9, shareDelta: 1 }) <= 100);
  assert.ok(momentumScore({ growth28: -1, growth7: -1, accel: -1, shareDelta: -1 }) >= 0);
});

test('shareSeries sums to 1 and starts after the regime start', () => {
  const members = [{ slug: 'a', series: series(200, () => 300) }, { slug: 'b', series: series(200, () => 100) }];
  const out = shareSeries(members, END, 26);
  assert.ok(out.dates.length > 20);
  for (let i = 0; i < out.dates.length; i++) assert.ok(Math.abs(out.series[0].share[i] + out.series[1].share[i] - 1) < 1e-9);
  assert.equal(out.series[0].share.at(-1), 0.75);
  const limited = shareSeries(members, END, 26, addDays(END, -60));
  assert.ok(limited.dates[0] >= addDays(END, -60 + 27));
});
