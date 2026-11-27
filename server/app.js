// HTTP application: public data API (/v1), account API (/api) and the web app.
import Fastify from 'fastify';
import cookie from '@fastify/cookie';
import fastifyStatic from '@fastify/static';
import fs from 'node:fs';
import path from 'node:path';
import { config, billingEnabled } from './config.js';
import { DIMENSIONS, FOLLOWER_BUCKETS, ValidationError, followerBucket, parseDeal, quarterOf, FIRST_QUARTER } from './domain.js';
import { K_MIN, anonymize, applyFilters, findCohort, groupBy, percentileRank, summarize } from './benchmarks.js';
import { TIERS, tierOf } from './plans.js';
import * as auth from './auth.js';
import * as billing from './billing.js';
import * as deals from './deals.js';

const clampInt = (v, lo, hi, dflt) => {
  const n = Number.parseInt(v, 10);
  return Number.isFinite(n) ? Math.min(hi, Math.max(lo, n)) : dflt;
};

class ApiError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export function buildApp(db, { logger = false } = {}) {
  const app = Fastify({ logger, trustProxy: config.trustProxy, bodyLimit: 256 * 1024 });
  app.register(cookie);

  // Keep the raw JSON text so Stripe webhook signatures can be verified.
  app.addContentTypeParser('application/json', { parseAs: 'string' }, (req, body, done) => {
    req.rawBody = body;
    if (!body) return done(null, {});
    try {
      done(null, JSON.parse(body));
    } catch {
      done(new ApiError(400, 'invalid_json', 'Request body is not valid JSON.'));
    }
  });

  app.addHook('onSend', async (req, reply) => {
    reply.header('x-content-type-options', 'nosniff');
    reply.header('x-frame-options', 'DENY');
    reply.header('referrer-policy', 'strict-origin-when-cross-origin');
    if (!req.url.startsWith('/v1/')) {
      reply.header('content-security-policy', "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'");
    }
  });

  app.setErrorHandler((err, req, reply) => {
    const status = err.status || err.statusCode || 500;
    if (status >= 500) req.log.error(err);
    reply.code(status).send({ error: { code: err.code && status < 500 ? String(err.code).toLowerCase() : status >= 500 ? 'internal_error' : 'bad_request', message: status >= 500 ? 'Something went wrong.' : err.message, ...(err.fields ? { fields: err.fields } : {}) } });
  });

  const anonLimiter = auth.createLimiter(120, 60_000);
  const authLimiter = auth.createLimiter(10, 60_000);

  const sessionUser = (req) => auth.userFromSession(db, req.cookies[auth.SESSION_COOKIE]);
  const setSession = (reply, userId) => {
    const s = auth.createSession(db, userId);
    reply.setCookie(auth.SESSION_COOKIE, s.token, { path: '/', httpOnly: true, sameSite: 'lax', secure: config.secureCookies, maxAge: s.maxAge });
  };

  // ------------------------------------------------------------------
  // Data API — /v1. Auth: "Authorization: Bearer rfk_…" (metered against the
  // tier's daily quota), the web session cookie, or anonymous.
  // ------------------------------------------------------------------
  /** Moderators need to see everything they moderate, so they get full access. */
  const accessOf = (user) => (user && config.adminEmails.includes(user.email.toLowerCase()) ? 'team' : tierOf(user, user ? deals.isContributor(db, user.id) : false));

  const FILTER_DIMS = ['sport', 'level', 'deal_type', 'payer_type', 'followers', 'industry', 'class_year', 'region', 'clearance'];
  const GROUP_DIMS = [...FILTER_DIMS, 'quarter'];

  const csvCell = (v) => (v === null || v === undefined ? '' : /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
  const toCsv = (cols, rows) => `${[cols.join(','), ...rows.map((r) => cols.map((c) => csvCell(r[c])).join(','))].join('\n')}\n`;

  app.register(async (v1) => {
    v1.addHook('onRequest', async (req, reply) => {
      reply.header('access-control-allow-origin', '*');
      reply.header('access-control-allow-headers', 'authorization, content-type');
      if (req.method === 'OPTIONS') return reply.code(204).send();
      const header = req.headers.authorization || '';
      let quota = null;
      if (header) {
        const user = header.startsWith('Bearer ') ? auth.userFromApiKey(db, header.slice(7).trim()) : null;
        if (!user) throw new ApiError(401, 'invalid_api_key', 'Invalid or revoked API key.');
        req.user = user;
        quota = auth.meter(db, user.id);
      } else {
        req.user = sessionUser(req);
        if (!anonLimiter(req.user ? `u${req.user.id}` : req.ip)) throw new ApiError(429, 'rate_limited', 'Too many requests. Slow down or use an API key.');
      }
      req.tierKey = accessOf(req.user);
      req.tier = TIERS[req.tierKey];
      reply.header('x-rangefinder-tier', req.tierKey);
      if (quota !== null) {
        reply.header('x-ratelimit-limit', req.tier.dailyRequests);
        reply.header('x-ratelimit-remaining', Math.max(0, req.tier.dailyRequests - quota));
        if (quota > req.tier.dailyRequests) throw new ApiError(429, 'quota_exceeded', `Daily quota of ${req.tier.dailyRequests} requests reached for the ${req.tier.name} tier. Resets at 00:00 UTC.`);
      }
    });
    v1.options('/*', async () => '');

    const need = (req, ability) => {
      if (!req.tier[ability]) throw new ApiError(402, 'access_required', 'Share one of your own deals to unlock this for free, or upgrade to Pro.');
    };
    /** Read and validate cohort filters from a query string or JSON body. */
    const filtersFrom = (src) => {
      const out = {};
      for (const dim of FILTER_DIMS) {
        const v = src[dim];
        if (v === undefined || v === '') continue;
        if (!Object.hasOwn(DIMENSIONS[dim], v)) throw new ApiError(400, 'invalid_filter', `Unknown ${dim}: ${v}`);
        out[dim] = v;
      }
      return out;
    };

    v1.get('/meta', async (req) => ({
      tier: req.tierKey,
      abilities: { explorer: req.tier.explorer, rangefinder: req.tier.rangefinder, comps: req.tier.comps, export: req.tier.export },
      k_min: K_MIN,
      dimensions: DIMENSIONS,
      follower_buckets: FOLLOWER_BUCKETS,
      quarters: { first: FIRST_QUARTER, current: quarterOf() },
      dataset: deals.datasetStats(db),
    }));

    // Public teaser: medians only, by sport and by deal type.
    v1.get('/summary', async () => {
      const all = deals.publishedDeals(db);
      const slim = (rows) => rows.map((r) => ({ key: r.key, label: r.label, n: r.n, median: r.median }));
      const overall = summarize(all);
      return {
        dataset: deals.datasetStats(db),
        overall: overall.suppressed ? { n: overall.n, suppressed: true } : { n: overall.n, median: overall.median },
        by_sport: slim(groupBy(all, 'sport')),
        by_deal_type: slim(groupBy(all, 'deal_type')),
      };
    });

    v1.get('/benchmarks', async (req) => {
      need(req, 'explorer');
      const groupDim = req.query.group_by || 'sport';
      if (!GROUP_DIMS.includes(groupDim)) throw new ApiError(400, 'invalid_group_by', `group_by must be one of: ${GROUP_DIMS.join(', ')}`);
      const filters = filtersFrom(req.query);
      const cohort = applyFilters(deals.publishedDeals(db), filters);
      return { filters, group_by: groupDim, k_min: K_MIN, overall: summarize(cohort), rows: groupBy(cohort, groupDim) };
    });

    v1.get('/comps', async (req) => {
      need(req, 'explorer');
      const filters = filtersFrom(req.query);
      const cohort = applyFilters(deals.publishedDeals(db), filters);
      const limit = clampInt(req.query.limit, 1, req.tier.comps, req.tier.comps);
      // Below the floor nothing is listed: a short list would point at individuals.
      const rows = cohort.length >= K_MIN ? [...cohort].sort((a, b) => (a.created_at < b.created_at ? 1 : -1)).slice(0, limit).map(anonymize) : [];
      return { filters, n: cohort.length, limit_cap: req.tier.comps, rows };
    });

    v1.post('/rangefinder', async (req) => {
      need(req, 'rangefinder');
      const body = req.body || {};
      for (const dim of ['sport', 'level', 'deal_type', 'payer_type']) {
        if (!Object.hasOwn(DIMENSIONS[dim], body[dim] ?? '')) throw new ApiError(400, 'invalid_profile', `Choose a valid ${dim.replace('_', ' ')}.`);
      }
      const followers = Number(body.followers);
      if (!Number.isInteger(followers) || followers < 0) throw new ApiError(400, 'invalid_profile', 'Enter total followers as a whole number.');
      const amount = body.amount === undefined || body.amount === null || body.amount === '' ? null : Number(body.amount);
      if (amount !== null && (!Number.isFinite(amount) || amount < 0)) throw new ApiError(400, 'invalid_amount', 'Amount must be a positive number.');

      const profile = { sport: body.sport, level: body.level, deal_type: body.deal_type, payer_type: body.payer_type, followers };
      const found = findCohort(deals.publishedDeals(db), profile);
      const stats = summarize(found.cohort);
      const result = {
        profile: { ...profile, followers_bucket: followerBucket(followers) },
        basis: { n: found.cohort.length, exact_match: found.widened.length === 0, widened: found.widened },
        stats,
        amount,
        percentile: null,
        position: null,
        comps: [],
      };
      if (stats.suppressed) return result;
      if (amount !== null) {
        result.percentile = percentileRank(found.cohort, amount);
        result.position = amount < stats.p25 ? 'below' : amount <= stats.p75 ? 'within' : stats.p90 === null || amount <= stats.p90 ? 'above' : 'well_above';
      }
      const anchor = amount ?? stats.median;
      result.comps = [...found.cohort].sort((a, b) => Math.abs(a.total_usd - anchor) - Math.abs(b.total_usd - anchor)).slice(0, req.tier.comps).map(anonymize);
      return result;
    });

    v1.get('/export/benchmarks.csv', async (req, reply) => {
      if (!req.tier.export) throw new ApiError(402, 'plan_required', 'CSV export is available on the Pro and Team plans.');
      const groupDim = GROUP_DIMS.includes(req.query.group_by) ? req.query.group_by : 'sport';
      const rows = groupBy(applyFilters(deals.publishedDeals(db), filtersFrom(req.query)), groupDim);
      return reply.header('content-type', 'text/csv; charset=utf-8').header('content-disposition', `attachment; filename="rangefinder-by-${groupDim}.csv"`)
        .send(toCsv(['key', 'label', 'n', 'p10', 'p25', 'median', 'p75', 'p90', 'cleared_rate', 'verified_share'], rows));
    });
  }, { prefix: '/v1' });

  // ------------------------------------------------------------------
  // Account API — /api. Cookie-authenticated, JSON only (a JSON content type
  // cannot be sent cross-site without a CORS preflight, which we never grant).
  // ------------------------------------------------------------------
  app.register(async (api) => {
    api.addHook('preHandler', async (req) => {
      if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.url !== '/api/billing/webhook' && !String(req.headers['content-type'] || '').startsWith('application/json')) {
        throw new ApiError(415, 'unsupported_media_type', 'Send JSON.');
      }
    });
    const requireUser = (req) => {
      const user = sessionUser(req);
      if (!user) throw new ApiError(401, 'unauthenticated', 'Sign in first.');
      return user;
    };
    const guard = (req) => {
      if (!authLimiter(req.ip)) throw new ApiError(429, 'rate_limited', 'Too many attempts. Try again in a minute.');
    };
    const wrap = (fn) => {
      try {
        return fn();
      } catch (err) {
        if (err instanceof auth.AuthError) throw new ApiError(err.status, 'invalid_request', err.message);
        throw err;
      }
    };

    api.get('/config', async () => ({
      billing: billingEnabled(),
      sales_email: config.salesEmail || null,
      tiers: Object.fromEntries(['contributor', 'pro', 'team'].map((k) => [k, { name: TIERS[k].name, price: TIERS[k].price, tagline: TIERS[k].tagline, features: TIERS[k].features }])),
    }));

    api.post('/auth/signup', async (req, reply) => {
      guard(req);
      const user = wrap(() => auth.createUser(db, req.body.email, req.body.password));
      setSession(reply, user.id);
      return { user };
    });

    api.post('/auth/login', async (req, reply) => {
      guard(req);
      const user = wrap(() => auth.authenticate(db, req.body.email, req.body.password));
      setSession(reply, user.id);
      return { user };
    });

    api.post('/auth/logout', async (req, reply) => {
      auth.destroySession(db, req.cookies[auth.SESSION_COOKIE]);
      reply.clearCookie(auth.SESSION_COOKIE, { path: '/' });
      return { ok: true };
    });

    api.post('/auth/password', async (req) => {
      guard(req);
      const user = requireUser(req);
      wrap(() => auth.changePassword(db, user.id, req.body.current, req.body.next, req.cookies[auth.SESSION_COOKIE]));
      return { ok: true };
    });

    const isAdmin = (user) => config.adminEmails.includes(user.email.toLowerCase());

    api.get('/me', async (req) => {
      const user = sessionUser(req);
      if (!user) return { user: null };
      const contributing = deals.isContributor(db, user.id);
      const tierKey = accessOf(user);
      return {
        user,
        tier: tierKey,
        tier_name: TIERS[tierKey].name,
        contributing,
        is_admin: isAdmin(user),
        limits: { daily_requests: TIERS[tierKey].dailyRequests, comps: TIERS[tierKey].comps, export: TIERS[tierKey].export },
        usage: auth.usageHistory(db, user.id),
        keys: auth.listApiKeys(db, user.id),
        deals: deals.myDeals(db, user.id),
      };
    });

    api.post('/deals', async (req) => {
      const user = requireUser(req);
      try {
        return { deal: deals.submitDeal(db, user.id, parseDeal(req.body)) };
      } catch (err) {
        if (err instanceof ValidationError) {
          const e = new ApiError(400, 'invalid_deal', err.message);
          e.fields = err.fields;
          throw e;
        }
        if (err instanceof deals.DealError) throw new ApiError(err.status, 'deal_refused', err.message);
        throw err;
      }
    });

    api.delete('/deals/:id', async (req) => {
      if (!deals.withdrawDeal(db, requireUser(req).id, Number(req.params.id))) throw new ApiError(404, 'not_found', 'No such deal.');
      return { ok: true };
    });

    const requireAdmin = (req) => {
      const user = requireUser(req);
      if (!isAdmin(user)) throw new ApiError(403, 'forbidden', 'Moderators only.');
      return user;
    };

    api.get('/admin/queue', async (req) => {
      requireAdmin(req);
      return { deals: deals.reviewQueue(db) };
    });

    api.post('/admin/deals/:id', async (req) => {
      requireAdmin(req);
      if (!['approve', 'verify', 'reject'].includes(req.body.action)) throw new ApiError(400, 'invalid_action', 'action must be approve, verify or reject.');
      if (!deals.reviewDeal(db, Number(req.params.id), req.body.action)) throw new ApiError(404, 'not_found', 'No such deal.');
      return { ok: true };
    });

    api.post('/keys', async (req) => wrap(() => ({ key: auth.createApiKey(db, requireUser(req).id, req.body.name) })));

    api.delete('/keys/:id', async (req) => {
      if (!auth.revokeApiKey(db, requireUser(req).id, Number(req.params.id))) throw new ApiError(404, 'not_found', 'No such key.');
      return { ok: true };
    });

    api.post('/billing/checkout', async (req) => {
      const user = requireUser(req);
      if (!billingEnabled()) throw new ApiError(503, 'billing_disabled', 'Billing is not configured on this deployment.');
      const plan = req.body.plan;
      if (!['pro', 'team'].includes(plan) || !config.stripe.prices[plan]) throw new ApiError(400, 'invalid_plan', 'Unknown plan.');
      return { url: await billing.createCheckout(user, plan) };
    });

    api.post('/billing/portal', async (req) => {
      const user = requireUser(req);
      const row = db.prepare('SELECT stripe_customer_id FROM users WHERE id = ?').get(user.id);
      if (!billingEnabled() || !row.stripe_customer_id) throw new ApiError(400, 'no_subscription', 'No active subscription.');
      return { url: await billing.createPortal(row.stripe_customer_id) };
    });

    api.post('/billing/webhook', async (req) => {
      if (!config.stripe.webhookSecret) throw new ApiError(503, 'billing_disabled', 'Webhook secret not configured.');
      let event;
      try {
        event = billing.verifyWebhook(req.rawBody || '', req.headers['stripe-signature'], config.stripe.webhookSecret);
      } catch (err) {
        throw new ApiError(400, 'invalid_signature', err.message);
      }
      return { received: true, result: billing.applyEvent(db, event) };
    });
  }, { prefix: '/api' });

  app.get('/healthz', async () => ({ ok: true, deals: deals.datasetStats(db).deals }));

  // ------------------------------------------------------------------
  // Web app (built by `npm run build` into web/dist) with SPA fallback.
  // ------------------------------------------------------------------
  const dist = path.join(config.root, 'web', 'dist');
  if (fs.existsSync(path.join(dist, 'index.html'))) {
    app.register(fastifyStatic, { root: dist, wildcard: false, maxAge: '1h', immutable: false });
    app.setNotFoundHandler((req, reply) => {
      if (req.method === 'GET' && !req.url.startsWith('/v1/') && !req.url.startsWith('/api/') && !path.extname(req.url.split('?')[0])) {
        return reply.header('cache-control', 'no-cache').sendFile('index.html');
      }
      reply.code(404).send({ error: { code: 'not_found', message: 'Not found.' } });
    });
  } else {
    app.setNotFoundHandler((req, reply) => reply.code(404).send({ error: { code: 'not_found', message: 'Not found.' } }));
  }

  return app;
}
