// Central configuration. Everything is overridable by environment variables.
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const env = process.env;
const int = (v, d) => (v === undefined || v === '' ? d : Number.parseInt(v, 10));

export const config = {
  root,
  env: env.NODE_ENV || 'development',
  port: int(env.PORT, 8080),
  host: env.HOST || '0.0.0.0',
  dbPath: env.DATABASE_PATH || path.join(root, 'data', 'uptake.db'),
  publicUrl: (env.PUBLIC_URL || `http://localhost:${int(env.PORT, 8080)}`).replace(/\/$/, ''),
  // Set to "1" when running behind a TLS-terminating proxy so cookies are Secure.
  secureCookies: env.SECURE_COOKIES === '1' || env.NODE_ENV === 'production',
  trustProxy: env.TRUST_PROXY === '1',
  // Collection
  collectOnBoot: env.COLLECT_ON_BOOT === '1',
  collectHourUtc: int(env.COLLECT_HOUR_UTC, 7), // daily run; upstream stats settle a few hours after midnight UTC
  schedulerEnabled: env.SCHEDULER !== '0',
  historyDays: int(env.HISTORY_DAYS, 365),
  hfModelLimit: int(env.HF_MODEL_LIMIT, 2000),
  userAgent: env.COLLECTOR_USER_AGENT || 'uptake-collector/0.1',
  // Billing (optional — the app runs without it; upgrade buttons are hidden)
  stripe: {
    secretKey: env.STRIPE_SECRET_KEY || '',
    webhookSecret: env.STRIPE_WEBHOOK_SECRET || '',
    prices: { pro: env.STRIPE_PRICE_PRO || '', team: env.STRIPE_PRICE_TEAM || '' },
  },
  salesEmail: env.SALES_EMAIL || '',
};

export const billingEnabled = () => Boolean(config.stripe.secretKey && config.stripe.prices.pro);
