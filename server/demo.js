// Synthetic sample data, for development and product demos ONLY.
//
//   node server/demo.js seed [count]   insert generated deals (default 1500)
//   node server/demo.js purge          remove every generated deal
//
// Generated rows are flagged is_demo and the site shows a banner while any
// exist. They are invented by the formulas below, not collected from anyone,
// and must be purged before real athletes or paying customers use the product.
import { pathToFileURL } from 'node:url';
import { config } from './config.js';
import { openDb, tx } from './db.js';
import { purgeDemo, submitDeal } from './deals.js';
import { quarterOf } from './domain.js';

/** Small seeded PRNG so a seed run is reproducible. */
function rng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const weighted = (r, table) => {
  const total = Object.values(table).reduce((a, b) => a + b, 0);
  let x = r() * total;
  for (const [k, w] of Object.entries(table)) if ((x -= w) <= 0) return k;
  return Object.keys(table)[0];
};
const normal = (r) => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * Math.PI * r());

const SPORT_MIX = { football: 30, mens_basketball: 14, womens_basketball: 10, baseball: 7, softball: 5, womens_volleyball: 6, womens_soccer: 4, mens_soccer: 3, gymnastics: 4, track_xc: 5, swim_dive: 3, wrestling: 3, lacrosse: 2, ice_hockey: 2, golf: 1, tennis: 1 };
const SPORT_VALUE = { football: 1.6, mens_basketball: 1.5, womens_basketball: 1.1, gymnastics: 1.2, baseball: 0.8, softball: 0.75, womens_volleyball: 0.85 };
const LEVEL_MIX = { power4: 34, group6: 16, d1: 26, d2: 12, d3: 8, naia_juco: 4 };
const LEVEL_VALUE = { power4: 2.2, group6: 1.2, d1: 1, d2: 0.6, d3: 0.45, naia_juco: 0.4 };
const TYPE_MIX = { social_post: 34, content: 14, appearance: 14, autograph: 8, camp: 7, licensing: 6, ambassador: 13, other: 4 };
const TYPE_VALUE = { social_post: 1, content: 1.1, appearance: 1.4, autograph: 0.9, camp: 1.3, licensing: 1.8, ambassador: 4.5, other: 1 };
const PAYER_MIX = { local_business: 36, national_brand: 20, collective: 24, school_partner: 8, marketplace: 12 };
const PAYER_VALUE = { local_business: 0.7, national_brand: 1.5, collective: 3.2, school_partner: 1.3, marketplace: 0.8 };

export function generateDeal(r, now = new Date()) {
  const sport = weighted(r, SPORT_MIX);
  const level = weighted(r, LEVEL_MIX);
  const deal_type = weighted(r, TYPE_MIX);
  const payer_type = weighted(r, PAYER_MIX);
  const followers = Math.round(Math.exp(7.6 + 1.5 * normal(r) + (level === 'power4' ? 0.9 : 0)));
  const base = 260 * (SPORT_VALUE[sport] || 0.7) * LEVEL_VALUE[level] * TYPE_VALUE[deal_type] * PAYER_VALUE[payer_type] * (1 + Math.log10(1 + followers / 2000)) ** 1.6;
  const total = Math.max(25, Math.round((base * Math.exp(0.75 * normal(r))) / 5) * 5);
  const inKind = r() < 0.22 ? Math.round((total * (0.3 + 0.7 * r())) / 5) * 5 : 0;
  const quartersBack = Math.floor(r() ** 1.7 * 10);
  const d = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() - 3 * quartersBack, 15));
  const sinceHouse = quarterOf(d) >= '2025-Q3';
  const overRange = payer_type === 'collective' && total > 20000;
  return {
    sport, level, deal_type, payer_type, followers,
    class_year: weighted(r, { fr: 18, so: 24, jr: 26, sr: 24, grad: 8 }),
    role: weighted(r, { starter: 55, rotation: 30, reserve: 15 }),
    region: weighted(r, { southeast: 28, midwest: 24, southwest: 16, west: 17, northeast: 15 }),
    industry: weighted(r, payer_type === 'local_business' ? { food_beverage: 30, auto: 18, local_services: 28, health_fitness: 12, financial: 6, other: 6 } : { apparel: 20, food_beverage: 18, tech: 14, health_fitness: 12, financial: 8, gaming: 8, media: 8, auto: 5, other: 7 }),
    deliverables: deal_type === 'ambassador' ? 4 + Math.floor(r() * 12) : 1 + Math.floor(r() ** 2 * 5),
    duration_months: deal_type === 'ambassador' ? 3 + Math.floor(r() * 10) : r() < 0.15 ? 1 + Math.floor(r() * 3) : 0,
    cash_usd: total - inKind, in_kind_usd: inKind, total_usd: total,
    exclusive: r() < (deal_type === 'ambassador' ? 0.45 : 0.08) ? 1 : 0,
    has_agent: r() < (total > 5000 ? 0.6 : 0.12) ? 1 : 0,
    clearance: total < 600 ? 'not_required' : !sinceHouse ? 'not_submitted' : weighted(r, overRange ? { cleared: 45, not_cleared: 35, pending: 12, not_submitted: 8 } : { cleared: 78, not_cleared: 5, pending: 9, not_submitted: 8 }),
    signed_quarter: quarterOf(d),
  };
}

export function seedDemo(db, count = 1500, seed = 20261127) {
  const r = rng(seed);
  const now = new Date();
  tx(db, () => {
    for (let i = 0; i < count; i++) submitDeal(db, null, generateDeal(r, now), { isDemo: true, now: new Date(now - Math.floor(r() * 200) * 86400e3) });
  });
  return count;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [cmd, arg] = process.argv.slice(2);
  const db = openDb(config.dbPath);
  if (cmd === 'seed') console.log(`Inserted ${seedDemo(db, Number(arg) || 1500)} synthetic demo deals. Remove them with: npm run demo:purge`);
  else if (cmd === 'purge') console.log(`Removed ${purgeDemo(db)} demo deals.`);
  else console.log('Usage: node server/demo.js seed [count] | purge');
  db.close();
}
