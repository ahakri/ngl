// HTTP application: public data API (/v1), account API (/api) and the web app.
import Fastify from 'fastify';
import cookie from '@fastify/cookie';
import fastifyStatic from '@fastify/static';
import fs from 'node:fs';
import path from 'node:path';
import { config, billingEnabled } from './config.js';
import { ECOSYSTEMS, categoryBySlug, projectBySlug } from './catalog.js';
import { PLANS, limitsOf, planOf } from './plans.js';
import * as auth from './auth.js';
import * as billing from './billing.js';
import * as q from './queries.js';

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
    reply.code(status).send({ error: { code: err.code && status < 500 ? String(err.code).toLowerCase() : status >= 500 ? 'internal_error' : 'bad_request', message: status >= 500 ? 'Something went wrong.' : err.message } });
  });

  const anonLimiter = auth.createLimiter(120, 60_000);
  const authLimiter = auth.createLimiter(10, 60_000);

  const sessionUser = (req) => auth.userFromSession(db, req.cookies[auth.SESSION_COOKIE]);
  const setSession = (reply, userId) => {
    const s = auth.createSession(db, userId);
    reply.setCookie(auth.SESSION_COOKIE, s.token, { path: '/', httpOnly: true, sameSite: 'lax', secure: config.secureCookies, maxAge: s.maxAge });
  };

  // ------------------------------------------------------------------
  // Data API — /v1. Auth: "Authorization: Bearer upk_…" (metered against the
  // plan's daily quota), the web session cookie, or anonymous (free limits).
  // ------------------------------------------------------------------
  app.register(async (v1) => {
    v1.addHook('onRequest', async (req, reply) => {
      reply.header('access-control-allow-origin', '*');
      reply.header('access-control-allow-headers', 'authorization');
      if (req.method === 'OPTIONS') return reply.code(204).send();
      const header = req.headers.authorization || '';
      if (header) {
        const user = header.startsWith('Bearer ') ? auth.userFromApiKey(db, header.slice(7).trim()) : null;
        if (!user) throw new ApiError(401, 'invalid_api_key', 'Invalid or revoked API key.');
        const limits = limitsOf(user);
        const used = auth.meter(db, user.id);
        reply.header('x-ratelimit-limit', limits.dailyRequests);
        reply.header('x-ratelimit-remaining', Math.max(0, limits.dailyRequests - used));
        if (used > limits.dailyRequests) throw new ApiError(429, 'quota_exceeded', `Daily quota of ${limits.dailyRequests} requests reached for the ${limits.name} plan. Resets at 00:00 UTC.`);
        req.user = user;
      } else {
        req.user = sessionUser(req);
        if (!anonLimiter(req.user ? `u${req.user.id}` : req.ip)) throw new ApiError(429, 'rate_limited', 'Too many requests. Slow down or use an API key.');
      }
      req.limits = limitsOf(req.user);
      reply.header('x-uptake-plan', planOf(req.user));
    });
    v1.options('/*', async () => '');

    const ecosystem = (req, dflt = 'pypi') => {
      const e = req.query.ecosystem || dflt;
      if (e !== null && !ECOSYSTEMS.includes(e)) throw new ApiError(400, 'invalid_ecosystem', `ecosystem must be one of: ${ECOSYSTEMS.join(', ')}`);
      return e;
    };
    const gated = (req, body) => ({ plan: planOf(req.user), ...body });

    v1.get('/meta', async (req) => gated(req, q.meta(db)));

    v1.get('/signals', async (req) => {
      const category = req.query.category;
      if (category && !categoryBySlug.has(category)) throw new ApiError(404, 'unknown_category', 'Unknown category.');
      return gated(req, { data: q.allSignals(db, { ecosystem: ecosystem(req, null) || undefined, category }) });
    });

    v1.get('/movers', async (req) => {
      const cap = req.limits.moversLimit;
      const limit = clampInt(req.query.limit, 1, cap, Math.min(10, cap));
      const direction = req.query.direction === 'down' ? 'down' : 'up';
      return gated(req, { ecosystem: ecosystem(req), direction, limit_cap: cap, data: q.movers(db, { ecosystem: ecosystem(req), direction, limit }) });
    });

    v1.get('/categories/:slug', async (req) => {
      const view = q.categoryView(db, req.params.slug, ecosystem(req), req.limits.shareWeeks);
      if (!view) throw new ApiError(404, 'unknown_category', 'Unknown category.');
      return gated(req, view);
    });

    v1.get('/projects/:slug', async (req) => {
      const days = clampInt(req.query.days, 7, req.limits.historyDays, Math.min(365, req.limits.historyDays));
      const view = q.projectView(db, req.params.slug, days);
      if (!view) throw new ApiError(404, 'unknown_project', 'Unknown project.');
      return gated(req, { history_days: days, history_cap_days: req.limits.historyDays, ...view });
    });

    v1.get('/models/:dim(orgs|tasks)', async (req) => {
      const dim = req.params.dim === 'orgs' ? 'org' : 'task';
      return gated(req, q.hfAggregate(db, dim, clampInt(req.query.limit, 1, req.limits.modelsLimit, 25)));
    });

    v1.get('/models', async (req) => {
      const sort = ['downloads', 'trending', 'likes'].includes(req.query.sort) ? req.query.sort : 'downloads';
      return gated(req, { sort, limit_cap: req.limits.modelsLimit, ...q.hfModels(db, sort, clampInt(req.query.limit, 1, req.limits.modelsLimit, 25)) });
    });

    const requireExport = (req) => {
      if (!req.limits.export) throw new ApiError(402, 'plan_required', 'CSV export is available on the Pro and Team plans.');
    };
    const sendCsv = (reply, name, csv) => reply.header('content-type', 'text/csv; charset=utf-8').header('content-disposition', `attachment; filename="${name}"`).send(csv);

    v1.get('/export/signals.csv', async (req, reply) => {
      requireExport(req);
      const rows = q.allSignals(db, { ecosystem: ecosystem(req, null) || undefined });
      return sendCsv(reply, 'uptake-signals.csv', q.toCsv(Object.keys(rows[0] || { project: 1 }), rows));
    });

    v1.get('/export/series.csv', async (req, reply) => {
      requireExport(req);
      const slug = req.query.project;
      if (!projectBySlug.has(slug)) throw new ApiError(404, 'unknown_project', 'Pass ?project=<slug>.');
      const view = q.projectView(db, slug, req.limits.historyDays);
      const rows = Object.entries(view.series).flatMap(([eco, pts]) => pts.map((pt) => ({ project: slug, ecosystem: eco, date: pt.date, downloads: pt.downloads })));
      return sendCsv(reply, `uptake-${slug}.csv`, q.toCsv(['project', 'ecosystem', 'date', 'downloads'], rows));
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
      plans: Object.fromEntries(Object.entries(PLANS).map(([k, p]) => [k, { name: p.name, price: p.price, tagline: p.tagline, features: p.features, daily_requests: p.dailyRequests }])),
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

    api.get('/me', async (req) => {
      const user = sessionUser(req);
      if (!user) return { user: null };
      const limits = limitsOf(user);
      return { user, limits: { daily_requests: limits.dailyRequests, history_days: limits.historyDays, export: limits.export }, usage: auth.usageHistory(db, user.id), keys: auth.listApiKeys(db, user.id) };
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

  app.get('/healthz', async () => {
    const run = db.prepare('SELECT finished_at, ok FROM runs WHERE finished_at IS NOT NULL ORDER BY id DESC LIMIT 1').get();
    return { ok: true, last_run: run || null };
  });

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
