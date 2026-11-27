// HTTP application: public data API (/v1), account API (/api) and the web app.
import Fastify from 'fastify';
import cookie from '@fastify/cookie';
import fastifyStatic from '@fastify/static';
import fs from 'node:fs';
import path from 'node:path';
import { config, billingEnabled } from './config.js';
import { TIERS, tierOf } from './plans.js';
import * as auth from './auth.js';
import * as billing from './billing.js';
import * as q from './queries.js';
import { buildDigest, digestMarkdown, subscribe } from './digest.js';

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
  // Data API — /v1. Auth: "Authorization: Bearer slk_…" (metered against the
  // tier's daily quota), the web session cookie, or anonymous (free tier).
  // ------------------------------------------------------------------
  const filtersOf = (src) => {
    try {
      return q.parseFilters(src);
    } catch (err) {
      if (err instanceof q.FilterError) throw new ApiError(400, 'invalid_filter', err.message);
      throw err;
    }
  };

  app.register(async (v1) => {
    v1.addHook('onRequest', async (req, reply) => {
      reply.header('access-control-allow-origin', '*');
      reply.header('access-control-allow-headers', 'authorization');
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
      req.tierKey = tierOf(req.user);
      req.tier = TIERS[req.tierKey];
      reply.header('x-siteline-tier', req.tierKey);
      if (quota !== null) {
        reply.header('x-ratelimit-limit', req.tier.dailyRequests);
        reply.header('x-ratelimit-remaining', Math.max(0, req.tier.dailyRequests - quota));
        if (quota > req.tier.dailyRequests) throw new ApiError(429, 'quota_exceeded', `Daily quota of ${req.tier.dailyRequests} requests reached for the ${req.tier.name} plan. Resets at 00:00 UTC.`);
      }
    });
    v1.options('/*', async () => '');

    v1.get('/meta', async (req) => ({
      tier: req.tierKey,
      abilities: { embargo_days: req.tier.embargoDays, upcoming: req.tier.upcoming, export: req.tier.export, watches: req.tier.watches, page_size: req.tier.pageSize },
      ...q.dimensions(),
    }));

    v1.get('/summary', async () => q.summary(db));
    // Public weekly digest: headlines only, so it can be shared freely.
    v1.get('/digest', async (req) => {
      const end = /^\d{4}-\d{2}-\d{2}$/.test(req.query.week_ending || '') ? req.query.week_ending : undefined;
      const d = buildDigest(db, end);
      return { ...d, markdown: digestMarkdown(d) };
    });

    v1.get('/jurisdictions', async () => ({ data: q.coverage(db) }));

    v1.get('/records', async (req) => {
      const limit = clampInt(req.query.limit, 1, req.tier.pageSize, Math.min(25, req.tier.pageSize));
      const offset = clampInt(req.query.offset, 0, 1_000_000, 0);
      const filters = filtersOf(req.query);
      const out = q.listRecords(db, filters, { limit, offset, embargoDays: req.tier.embargoDays });
      return { filters, limit, offset, total: out.total, withheld_by_plan: out.withheld, embargo_days: req.tier.embargoDays, data: out.rows };
    });

    v1.get('/records/:id', async (req) => {
      const rec = q.getRecord(db, Number(req.params.id), req.tier.embargoDays);
      if (!rec) throw new ApiError(404, 'not_found', 'No such record.');
      if (rec.embargoed) throw new ApiError(402, 'plan_required', `Records from the last ${req.tier.embargoDays} days are available on the Pro and Team plans.`);
      return rec;
    });

    v1.get('/upcoming', async (req) => {
      if (!req.tier.upcoming) throw new ApiError(402, 'plan_required', 'The upcoming hearings calendar is available on the Pro and Team plans.');
      return { data: q.upcoming(db, filtersOf(req.query)) };
    });

    v1.get('/export/records.csv', async (req, reply) => {
      if (!req.tier.export) throw new ApiError(402, 'plan_required', 'CSV export is available on the Pro and Team plans.');
      const out = q.listRecords(db, filtersOf(req.query), { limit: 100000, offset: 0, embargoDays: 0 });
      return reply.header('content-type', 'text/csv; charset=utf-8').header('content-disposition', 'attachment; filename="siteline-records.csv"').send(q.recordsCsv(out.rows));
    });
  }, { prefix: '/v1' });

  // Private alert feed for a saved watch. The token in the URL is the credential.
  app.get('/feeds/:token', async (req, reply) => {
    const watch = q.watchByToken(db, req.params.token);
    if (!watch) throw new ApiError(404, 'not_found', 'No such feed.');
    const tier = TIERS[tierOf({ plan: watch.plan })];
    if (!tier.watches) throw new ApiError(402, 'plan_required', 'This feed belongs to an account without an active Pro or Team plan.');
    const rows = q.listRecords(db, watch.filters, { limit: 50, embargoDays: 0 }).rows;
    return reply.header('content-type', 'application/atom+xml; charset=utf-8').send(q.atomFeed(watch, rows, config.publicUrl));
  });

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
      tiers: Object.fromEntries(Object.entries(TIERS).map(([k, t]) => [k, { name: t.name, price: t.price, tagline: t.tagline, features: t.features }])),
    }));

    api.post('/subscribe', async (req) => {
      guard(req);
      const result = subscribe(db, req.body.email);
      if (result === 'invalid') throw new ApiError(400, 'invalid_email', 'Enter a valid email address.');
      return { ok: true }; // same answer whether new or already subscribed
    });

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

    api.get('/me', async (req) => {
      const user = sessionUser(req);
      if (!user) return { user: null };
      const tierKey = tierOf(user);
      return {
        user,
        tier: tierKey,
        tier_name: TIERS[tierKey].name,
        limits: { daily_requests: TIERS[tierKey].dailyRequests, watches: TIERS[tierKey].watches, export: TIERS[tierKey].export },
        usage: auth.usageHistory(db, user.id),
        keys: auth.listApiKeys(db, user.id),
        watches: q.listWatches(db, user.id).map((w) => ({ ...w, feed_url: `${config.publicUrl}/feeds/${w.feed_token}`, feed_token: undefined })),
      };
    });

    api.post('/watches', async (req) => {
      const user = requireUser(req);
      try {
        const w = q.createWatch(db, user.id, req.body.name, q.parseFilters(req.body.filters || {}), TIERS[tierOf(user)].watches);
        return { watch: { id: w.id, name: w.name, filters: w.filters, feed_url: `${config.publicUrl}/feeds/${w.feed_token}` } };
      } catch (err) {
        if (err instanceof q.FilterError) throw new ApiError(TIERS[tierOf(user)].watches ? 400 : 402, 'watch_refused', err.message);
        throw err;
      }
    });

    api.delete('/watches/:id', async (req) => {
      if (!q.deleteWatch(db, requireUser(req).id, Number(req.params.id))) throw new ApiError(404, 'not_found', 'No such watch.');
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

  app.get('/healthz', async () => ({ ok: true, last_sync: db.prepare('SELECT MAX(last_ok) AS t FROM sync').get().t }));

  // ------------------------------------------------------------------
  // Web app (built by `npm run build` into web/dist) with SPA fallback.
  // ------------------------------------------------------------------
  const dist = path.join(config.root, 'web', 'dist');
  if (fs.existsSync(path.join(dist, 'index.html'))) {
    app.register(fastifyStatic, { root: dist, wildcard: false, maxAge: '1h', immutable: false });
    app.setNotFoundHandler((req, reply) => {
      if (req.method === 'GET' && !req.url.startsWith('/v1/') && !req.url.startsWith('/api/') && !req.url.startsWith('/feeds/') && !path.extname(req.url.split('?')[0])) {
        return reply.header('cache-control', 'no-cache').sendFile('index.html');
      }
      reply.code(404).send({ error: { code: 'not_found', message: 'Not found.' } });
    });
  } else {
    app.setNotFoundHandler((req, reply) => reply.code(404).send({ error: { code: 'not_found', message: 'Not found.' } }));
  }

  return app;
}
