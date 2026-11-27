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
  publicUrl: (env.PUBLIC_URL || `http://localhost:${int(env.PORT, 8080)}`).replace(/\/$/, ''),
  // Set to "1" when running behind a TLS-terminating proxy so cookies are Secure.
  secureCookies: env.SECURE_COOKIES === '1' || env.NODE_ENV === 'production',
  trustProxy: env.TRUST_PROXY === '1',
  dbPath: env.DATABASE_PATH || path.join(root, 'data', 'siteline.db'),
  // Collection
  schedulerEnabled: env.SCHEDULER !== '0',
  collectHourUtc: int(env.COLLECT_HOUR_UTC, 9),
  // Billing (optional — the app runs without it; upgrade buttons are hidden)
  stripe: {
    secretKey: env.STRIPE_SECRET_KEY || '',
    webhookSecret: env.STRIPE_WEBHOOK_SECRET || '',
    prices: { pro: env.STRIPE_PRICE_PRO || '', team: env.STRIPE_PRICE_TEAM || '' },
  },
  salesEmail: env.SALES_EMAIL || '',
};

export const billingEnabled = () => Boolean(config.stripe.secretKey && config.stripe.prices.pro);
