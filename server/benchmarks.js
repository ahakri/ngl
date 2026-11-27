// The statistics Rangefinder sells: percentile bands over cohorts of deals,
// with a hard floor on cohort size so no individual deal can be inferred.
import { DIMENSIONS, FOLLOWER_BUCKETS, followerBucket } from './domain.js';

/** No statistic is ever published for fewer deals than this. */
export const K_MIN = 5;
/** The 10th and 90th percentiles are only published for cohorts at least this large: in a tiny cohort they are close to individual deals. */
export const K_TAILS = 10;
/** The range finder prefers a cohort at least this large before it stops widening. */
export const K_TARGET = 12;

/** Linear-interpolated percentile of an ascending-sorted array. */
export function percentile(sorted, p) {
  if (!sorted.length) return null;
  const idx = (sorted.length - 1) * p;
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
}

/** Summary of a cohort, or a suppressed stub when it is below K_MIN. */
export function summarize(deals) {
  const n = deals.length;
  if (n < K_MIN) return { n, suppressed: true };
  const totals = deals.map((d) => d.total_usd).sort((a, b) => a - b);
  const decided = deals.filter((d) => d.clearance === 'cleared' || d.clearance === 'not_cleared');
  const round = (v) => Math.round(v);
  return {
    n,
    suppressed: false,
    p10: n >= K_TAILS ? round(percentile(totals, 0.1)) : null,
    p25: round(percentile(totals, 0.25)),
    median: round(percentile(totals, 0.5)),
    p75: round(percentile(totals, 0.75)),
    p90: n >= K_TAILS ? round(percentile(totals, 0.9)) : null,
    // Share of deals with a known NIL Go decision that were cleared.
    cleared_rate: decided.length >= K_MIN ? decided.filter((d) => d.clearance === 'cleared').length / decided.length : null,
    verified_share: deals.filter((d) => d.verified).length / n,
  };
}

const valueOf = (deal, dim) => (dim === 'followers' ? followerBucket(deal.followers) : dim === 'quarter' ? deal.signed_quarter : deal[dim]);

/** Keep deals matching every filter. A filter value may be a string or an array of allowed values. */
export function applyFilters(deals, filters) {
  const active = Object.entries(filters).filter(([, v]) => v !== undefined && v !== null && v !== '' && !(Array.isArray(v) && !v.length));
  return deals.filter((d) => active.every(([dim, v]) => (Array.isArray(v) ? v.includes(valueOf(d, dim)) : valueOf(d, dim) === v)));
}

/** One summary row per value of `dim`, largest cohorts first. Suppressed cohorts are dropped. */
export function groupBy(deals, dim) {
  const groups = new Map();
  for (const d of deals) {
    const k = valueOf(d, dim);
    if (k === null || k === undefined) continue;
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(d);
  }
  const rows = [...groups].map(([key, members]) => ({ key, label: DIMENSIONS[dim]?.[key] || key, ...summarize(members) })).filter((r) => !r.suppressed);
  if (dim === 'quarter') return rows.sort((a, b) => (a.key < b.key ? -1 : 1));
  if (dim === 'followers') return rows.sort((a, b) => FOLLOWER_BUCKETS.findIndex((x) => x.key === a.key) - FOLLOWER_BUCKETS.findIndex((x) => x.key === b.key));
  return rows.sort((a, b) => b.n - a.n);
}

const adjacentBuckets = (key) => {
  const i = FOLLOWER_BUCKETS.findIndex((b) => b.key === key);
  return FOLLOWER_BUCKETS.slice(Math.max(0, i - 1), i + 2).map((b) => b.key);
};

/**
 * Find the tightest cohort of comparable deals that is large enough to quote.
 * Starts from an exact match and widens one step at a time, least important
 * attribute first, recording every step so the basis is auditable.
 */
export function findCohort(deals, profile) {
  const bucket = followerBucket(profile.followers);
  const exact = { sport: profile.sport, level: profile.level, deal_type: profile.deal_type, payer_type: profile.payer_type, followers: bucket };
  const ladder = [
    { filters: exact, widened: [] },
    { filters: { ...exact, payer_type: undefined }, widened: ['any payer type'] },
    { filters: { ...exact, payer_type: undefined, followers: adjacentBuckets(bucket) }, widened: ['any payer type', 'neighbouring follower ranges'] },
    { filters: { sport: profile.sport, deal_type: profile.deal_type, followers: adjacentBuckets(bucket) }, widened: ['any payer type', 'neighbouring follower ranges', 'any competition level'] },
    { filters: { sport: profile.sport, deal_type: profile.deal_type }, widened: ['any payer type', 'any follower count', 'any competition level'] },
    { filters: { deal_type: profile.deal_type, followers: adjacentBuckets(bucket) }, widened: ['any payer type', 'neighbouring follower ranges', 'any competition level', 'any sport'] },
    { filters: { deal_type: profile.deal_type }, widened: ['any payer type', 'any follower count', 'any competition level', 'any sport'] },
  ];
  let best = null;
  for (const step of ladder) {
    const cohort = applyFilters(deals, step.filters);
    if (cohort.length >= K_TARGET) return { cohort, ...step };
    if (!best && cohort.length >= K_MIN) best = { cohort, ...step };
  }
  return best || { cohort: [], filters: {}, widened: [] };
}

/** Where `amount` sits in the cohort: share of comparable deals at or below it (0–1). */
export function percentileRank(deals, amount) {
  if (!deals.length) return null;
  return deals.filter((d) => d.total_usd <= amount).length / deals.length;
}

const sig2 = (v) => {
  if (v <= 0) return 0;
  const mag = 10 ** Math.max(0, Math.floor(Math.log10(v)) - 1);
  return Math.round(v / mag) * mag;
};

/** A deal as shown to other members: bucketed and rounded, never exact. */
export function anonymize(deal) {
  return {
    sport: deal.sport,
    level: deal.level,
    class_year: deal.class_year,
    followers: followerBucket(deal.followers),
    payer_type: deal.payer_type,
    industry: deal.industry,
    deal_type: deal.deal_type,
    deliverables: deal.deliverables,
    duration_months: deal.duration_months,
    exclusive: Boolean(deal.exclusive),
    total_usd: sig2(deal.total_usd),
    in_kind: deal.in_kind_usd > 0,
    clearance: deal.clearance,
    signed_quarter: deal.signed_quarter,
    verified: Boolean(deal.verified),
  };
}

/**
 * Quality screen run on every submission. Anything flagged waits for a human.
 * @returns {string[]} reasons; empty means it can be published automatically
 */
export function screen(deal, existing) {
  const flags = [];
  if (deal.total_usd >= 250_000) flags.push('Total is $250K or more');
  if (deal.followers < 5_000 && deal.total_usd >= 50_000 && deal.payer_type !== 'collective') flags.push('Large payment for a small audience');
  if (deal.clearance === 'not_required' && deal.total_usd >= 600) flags.push('Marked "under $600" but total is $600 or more');
  const peers = applyFilters(existing, { sport: deal.sport, deal_type: deal.deal_type });
  if (peers.length >= 20) {
    const totals = peers.map((d) => d.total_usd).sort((a, b) => a - b);
    if (deal.total_usd > percentile(totals, 0.5) * 40) flags.push('More than 40× the median for this sport and deal type');
  }
  return flags;
}
