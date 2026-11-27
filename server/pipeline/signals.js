// Turns raw daily download series into the signals Uptake sells:
// growth, acceleration, category market share, rank and a momentum score.
//
// All windows are multiples of 7 days so weekday seasonality cancels out.
import { addDays } from '../db.js';

/** Sum of a Map<date, value> over [end-len+1, end]. Missing days count as 0. */
export function windowSum(series, end, len) {
  let total = 0;
  for (let i = 0; i < len; i++) total += series.get(addDays(end, -i)) || 0;
  return total;
}

const firstDate = (series) => {
  let min = null;
  for (const d of series.keys()) if (min === null || d < min) min = d;
  return min;
};

/** Relative change, or null when the base window isn't fully covered / is empty. */
function growth(series, end, len, start) {
  const baseStart = addDays(end, -(2 * len) + 1);
  if (!start || start > baseStart) return null;
  const base = windowSum(series, addDays(end, -len), len);
  if (base <= 0) return null;
  return windowSum(series, end, len) / base - 1;
}

/**
 * Detect registry-wide counting changes ("structural breaks"): dates where the
 * aggregate daily volume of an ecosystem shifts level by more than `threshold`
 * and stays there for four weeks. These are methodology changes upstream (bot
 * filtering, mirror reclassification), not adoption, so growth and share must
 * never be computed across one.
 * @param {Map<string, number>} total  date → aggregate value
 * @returns {{date:string, ratio:number}[]}  first day of each new regime
 */
export function detectBreaks(total, threshold = 1.3) {
  const dates = [...total.keys()].sort();
  if (dates.length < 63) return [];
  const beyond = (r) => r > 0 && Math.abs(Math.log(r)) > Math.log(threshold);
  const weeks = (end) => [0, 1, 2, 3].map((k) => windowSum(total, addDays(end, -7 * k), 7));
  const spread = (xs) => Math.max(...xs) / Math.max(Math.min(...xs), 1e-9);
  const median = (xs) => { const s = [...xs].sort((x, y) => x - y); return (s[1] + s[2]) / 2; };
  const candidates = [];
  for (const d of dates.slice(28, dates.length - 27)) {
    const pre = weeks(addDays(d, -1));       // four weeks ending the day before
    const post = weeks(addDays(d, 27));      // four weeks starting on d
    // A break is a step between two flat levels. Holidays fail the flatness
    // test (the dip sits inside one of the windows); organic growth fails the
    // sharpness test (no single week-over-week jump).
    if (spread(pre) > 1.25 || spread(post) > 1.25) continue;
    const step = post[3] / pre[0];           // first week after vs last week before
    const level = median(post) / median(pre);
    if (beyond(step) && beyond(level) && Math.sign(Math.log(step)) === Math.sign(Math.log(level))) {
      const day = (total.get(d) || 0) / Math.max(total.get(addDays(d, -7)) || 0, 1e-9); // sharpest single day
      candidates.push({ date: d, ratio: level, sharp: Math.abs(Math.log(day || 1e-9)) });
    }
  }
  // Adjacent days all "see" the same step; keep the day with the sharpest change.
  const out = [];
  for (const c of candidates) {
    const last = out.at(-1);
    if (last && addDays(last.date, 14) >= c.date) {
      if (c.sharp > last.sharp) out[out.length - 1] = c;
    } else out.push(c);
  }
  return out.map((b) => ({ date: b.date, ratio: Math.round(b.ratio * 1000) / 1000 }));
}

/**
 * Days on which the registry itself reported (almost) nothing — upstream
 * outages, not real behaviour. Judged on the ecosystem aggregate against the
 * same weekday one week either side.
 * @param {Map<string, number>} total
 * @returns {Set<string>}
 */
export function detectGaps(total) {
  const gaps = new Set();
  for (const [d, v] of total) {
    const around = [total.get(addDays(d, -7)), total.get(addDays(d, 7))].filter((x) => x > 0);
    if (around.length && v < 0.25 * Math.min(...around)) gaps.add(d);
  }
  return gaps;
}

/** Copy of `series` with gap days replaced by the mean of the nearest same-weekday values. */
export function fillGaps(series, gaps) {
  if (!gaps.size) return series;
  const out = new Map(series);
  for (const d of gaps) {
    if (!series.has(d)) continue;
    const near = [];
    for (const dir of [-1, 1]) {
      for (let k = 1; k <= 3; k++) {
        const n = addDays(d, dir * 7 * k);
        if (!gaps.has(n) && series.has(n)) { near.push(series.get(n)); break; }
      }
    }
    if (near.length) out.set(d, Math.round(near.reduce((x, y) => x + y, 0) / near.length));
  }
  return out;
}

/**
 * Latest date for which at least `quorum` of the active series have a value.
 * Registries publish with a lag, and not all packages update at once.
 */
export function pickAsOf(seriesList, quorum = 0.8) {
  const lastDates = seriesList.map((s) => [...s.keys()].sort().at(-1)).filter(Boolean).sort();
  if (!lastDates.length) return null;
  const newest = lastDates.at(-1);
  const active = seriesList.filter((s) => [...s.keys()].some((d) => d >= addDays(newest, -14)));
  for (let i = 0; i < 14; i++) {
    const d = addDays(newest, -i);
    const have = active.filter((s) => s.has(d)).length;
    if (have >= Math.ceil(active.length * quorum)) return d;
  }
  return newest;
}

/** 0–100. 50 = flat. Bounded so one outlier can't dominate a ranking. */
export function momentumScore({ growth28, growth7, accel, shareDelta }) {
  if (growth28 === null) return null;
  const x = 1.6 * growth28 + 0.6 * (growth7 ?? 0) + 0.5 * (accel ?? 0) + 8 * (shareDelta ?? 0);
  return Math.round((50 + 50 * Math.tanh(x)) * 10) / 10;
}

const MIN_BREAKOUT_VOLUME = 10000; // 28-day downloads; below this growth rates are noise

/**
 * @param {{slug:string, series:Map<string,number>}[]} members  one competitive set (category × ecosystem)
 * @param {string} asOf
 * @param {string|null} regimeStart  date of the latest structural break, if any
 * @returns signal rows, ranked by trailing-28-day volume
 */
export function computeCategorySignals(members, asOf, regimeStart = null) {
  const rows = members
    .filter((m) => m.series.size)
    .map((m) => {
      const first = firstDate(m.series);
      const start = regimeStart && regimeStart > first ? regimeStart : first;
      const d28 = windowSum(m.series, asOf, 28);
      const p28 = windowSum(m.series, addDays(asOf, -28), 28);
      const g28 = growth(m.series, asOf, 28, start);
      const g28prev = growth(m.series, addDays(asOf, -28), 28, start);
      return {
        project: m.slug,
        as_of: asOf,
        d7: windowSum(m.series, asOf, 7),
        d28,
        p28,
        growth_7d: growth(m.series, asOf, 7, start),
        growth_28d: g28,
        growth_12w: growth(m.series, asOf, 84, start),
        accel: g28 !== null && g28prev !== null ? g28 - g28prev : null,
      };
    });

  const total = rows.reduce((s, r) => s + r.d28, 0);
  const prevTotal = rows.reduce((s, r) => s + r.p28, 0);
  const prevRank = new Map([...rows].sort((a, b) => b.p28 - a.p28).map((r, i) => [r.project, i + 1]));

  rows.sort((a, b) => b.d28 - a.d28);
  return rows.map((r, i) => {
    const share = total > 0 ? r.d28 / total : null;
    const prevShare = prevTotal > 0 ? r.p28 / prevTotal : null;
    const shareDelta = share !== null && prevShare !== null ? share - prevShare : null;
    const momentum = momentumScore({ growth28: r.growth_28d, growth7: r.growth_7d, accel: r.accel, shareDelta });
    const breakout =
      r.growth_28d !== null && r.growth_28d >= 0.2 && (r.accel ?? 0) > 0 && (shareDelta ?? 0) > 0 && r.d28 >= MIN_BREAKOUT_VOLUME;
    const { p28, ...rest } = r;
    return {
      ...rest,
      share,
      share_delta_28d: shareDelta,
      momentum,
      rank: i + 1,
      rank_delta_28d: r.p28 > 0 ? prevRank.get(r.project) - (i + 1) : null, // positive = climbed
      breakout: breakout ? 1 : 0,
    };
  });
}

/**
 * Weekly market-share series for one competitive set: trailing-28-day share,
 * sampled every 7 days back from asOf.
 * @returns {{dates:string[], series:{slug:string, share:number[], volume:number[]}[]}}
 */
export function shareSeries(members, asOf, weeks = 26, regimeStart = null) {
  const first = members.map((m) => firstDate(m.series)).filter(Boolean).sort()[0];
  const earliest = regimeStart && regimeStart > first ? regimeStart : first;
  const dates = [];
  for (let w = weeks - 1; w >= 0; w--) {
    const d = addDays(asOf, -7 * w);
    if (earliest && addDays(d, -27) >= earliest) dates.push(d);
  }
  const volumes = members.map((m) => dates.map((d) => windowSum(m.series, d, 28)));
  const totals = dates.map((_, i) => volumes.reduce((s, v) => s + v[i], 0));
  return {
    dates,
    series: members.map((m, k) => ({
      slug: m.slug,
      volume: volumes[k],
      share: volumes[k].map((v, i) => (totals[i] > 0 ? v / totals[i] : 0)),
    })),
  };
}
