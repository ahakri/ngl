// The vocabulary of an NIL deal: every field a submission can carry, and how
// it is validated. Deliberately absent: athlete name, school, team, and brand
// name. Rangefinder never collects them, so it can never leak them.
export const SPORTS = {
  football: 'Football',
  mens_basketball: "Men's basketball",
  womens_basketball: "Women's basketball",
  baseball: 'Baseball',
  softball: 'Softball',
  womens_volleyball: "Women's volleyball",
  mens_soccer: "Men's soccer",
  womens_soccer: "Women's soccer",
  gymnastics: 'Gymnastics',
  track_xc: 'Track & cross country',
  swim_dive: 'Swimming & diving',
  wrestling: 'Wrestling',
  lacrosse: 'Lacrosse',
  ice_hockey: 'Ice hockey',
  golf: 'Golf',
  tennis: 'Tennis',
  other: 'Other sport',
};

export const LEVELS = {
  power4: 'Power 4',
  group6: 'Other FBS',
  d1: 'Other Division I',
  d2: 'Division II',
  d3: 'Division III',
  naia_juco: 'NAIA / JUCO',
};

export const CLASS_YEARS = { fr: 'Freshman', so: 'Sophomore', jr: 'Junior', sr: 'Senior', grad: 'Graduate' };
export const ROLES = { starter: 'Starter', rotation: 'Rotation player', reserve: 'Reserve' };
export const REGIONS = { northeast: 'Northeast', southeast: 'Southeast', midwest: 'Midwest', southwest: 'Southwest', west: 'West' };

export const PAYER_TYPES = {
  national_brand: 'National brand',
  local_business: 'Local or regional business',
  collective: 'Collective',
  school_partner: 'School-affiliated partner',
  marketplace: 'Marketplace or agency campaign',
};

export const INDUSTRIES = {
  apparel: 'Apparel & footwear',
  food_beverage: 'Food & beverage',
  auto: 'Automotive',
  financial: 'Financial services',
  tech: 'Tech & apps',
  health_fitness: 'Health & fitness',
  local_services: 'Local services',
  gaming: 'Gaming',
  media: 'Media & entertainment',
  other: 'Other',
};

export const DEAL_TYPES = {
  social_post: 'Social media post(s)',
  content: 'Content creation / UGC',
  appearance: 'Appearance or event',
  autograph: 'Autographs & memorabilia',
  camp: 'Camps & lessons',
  licensing: 'Licensing & merchandise',
  ambassador: 'Ambassador / long-term',
  other: 'Other',
};

export const CLEARANCE = {
  cleared: 'Cleared by NIL Go',
  not_cleared: 'Not cleared',
  pending: 'Submitted, awaiting decision',
  not_submitted: 'Not submitted',
  not_required: 'Not required (under $600)',
};

// Lower bound of each follower bucket, ascending.
export const FOLLOWER_BUCKETS = [
  { key: 'under_1k', min: 0, label: 'Under 1K' },
  { key: '1k_5k', min: 1_000, label: '1K–5K' },
  { key: '5k_10k', min: 5_000, label: '5K–10K' },
  { key: '10k_50k', min: 10_000, label: '10K–50K' },
  { key: '50k_100k', min: 50_000, label: '50K–100K' },
  { key: '100k_500k', min: 100_000, label: '100K–500K' },
  { key: '500k_plus', min: 500_000, label: '500K+' },
];
export const followerBucket = (n) => FOLLOWER_BUCKETS.findLast((b) => n >= b.min).key;
export const FOLLOWERS = Object.fromEntries(FOLLOWER_BUCKETS.map((b) => [b.key, b.label]));

export const DIMENSIONS = {
  sport: SPORTS,
  level: LEVELS,
  deal_type: DEAL_TYPES,
  payer_type: PAYER_TYPES,
  followers: FOLLOWERS,
  industry: INDUSTRIES,
  class_year: CLASS_YEARS,
  region: REGIONS,
  clearance: CLEARANCE,
};

export const FIRST_QUARTER = '2021-Q3'; // NIL became permitted on 1 July 2021
export const quarterOf = (d = new Date()) => `${d.getUTCFullYear()}-Q${Math.floor(d.getUTCMonth() / 3) + 1}`;

export class ValidationError extends Error {
  constructor(fields) {
    super(Object.values(fields)[0]);
    this.fields = fields;
    this.status = 400;
  }
}

const MAX_USD = 20_000_000;

/**
 * Validate and normalise a deal submission. Throws ValidationError with a
 * message per bad field.
 */
export function parseDeal(input, now = new Date()) {
  const e = {};
  const pick = (field, table, label, required = true) => {
    const v = input?.[field];
    if (v === undefined || v === null || v === '') {
      if (required) e[field] = `Choose ${label}.`;
      return null;
    }
    if (!Object.hasOwn(table, v)) e[field] = `Unknown ${label}.`;
    return v;
  };
  const money = (field, label) => {
    const raw = input?.[field];
    const v = raw === undefined || raw === null || raw === '' ? 0 : Number(raw);
    if (!Number.isFinite(v) || v < 0 || v > MAX_USD) e[field] = `${label} must be between $0 and $${MAX_USD.toLocaleString('en-US')}.`;
    return Math.round(v);
  };
  const int = (field, label, lo, hi, dflt) => {
    const raw = input?.[field];
    if (raw === undefined || raw === null || raw === '') {
      if (dflt === undefined) e[field] = `Enter ${label}.`;
      return dflt;
    }
    const v = Number(raw);
    if (!Number.isInteger(v) || v < lo || v > hi) e[field] = `${label} must be a whole number from ${lo.toLocaleString('en-US')} to ${hi.toLocaleString('en-US')}.`;
    return v;
  };

  const deal = {
    sport: pick('sport', SPORTS, 'a sport'),
    level: pick('level', LEVELS, 'a competition level'),
    class_year: pick('class_year', CLASS_YEARS, 'a class year'),
    role: pick('role', ROLES, 'a role', false),
    region: pick('region', REGIONS, 'a region'),
    followers: int('followers', 'Total followers', 0, 500_000_000),
    payer_type: pick('payer_type', PAYER_TYPES, 'who paid'),
    industry: pick('industry', INDUSTRIES, 'an industry'),
    deal_type: pick('deal_type', DEAL_TYPES, 'a deal type'),
    deliverables: int('deliverables', 'Deliverables', 1, 500, 1),
    duration_months: int('duration_months', 'Duration', 0, 60, 0),
    cash_usd: money('cash_usd', 'Cash'),
    in_kind_usd: money('in_kind_usd', 'In-kind value'),
    exclusive: input?.exclusive ? 1 : 0,
    has_agent: input?.has_agent ? 1 : 0,
    clearance: pick('clearance', CLEARANCE, 'the NIL Go outcome'),
    signed_quarter: String(input?.signed_quarter || ''),
  };
  deal.total_usd = deal.cash_usd + deal.in_kind_usd;
  if (!e.cash_usd && !e.in_kind_usd && deal.total_usd <= 0) e.cash_usd = 'Enter what the deal paid, in cash or in kind.';
  if (!/^\d{4}-Q[1-4]$/.test(deal.signed_quarter) || deal.signed_quarter < FIRST_QUARTER || deal.signed_quarter > quarterOf(now)) {
    e.signed_quarter = `Signing quarter must be between ${FIRST_QUARTER} and ${quarterOf(now)}.`;
  }
  if (input?.attest_adult !== true) e.attest_adult = 'You must confirm you are 18 or older.';
  if (input?.attest_right !== true) e.attest_right = 'You must confirm this is your own deal and you may share its terms.';
  if (Object.keys(e).length) throw new ValidationError(e);
  return deal;
}
