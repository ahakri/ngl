// Stripe billing over the REST API (no SDK dependency). Optional: when no
// STRIPE_SECRET_KEY is configured every function here reports "disabled".
import crypto from 'node:crypto';
import { config } from './config.js';

const API = 'https://api.stripe.com/v1';

async function stripe(path, params) {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { authorization: `Bearer ${config.stripe.secretKey}`, 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams(params),
    signal: AbortSignal.timeout(20000),
  });
  const body = await res.json();
  if (!res.ok) throw new Error(`Stripe: ${body.error?.message || res.status}`);
  return body;
}

export function planForPrice(priceId) {
  const { pro, team } = config.stripe.prices;
  if (priceId && priceId === pro) return 'pro';
  if (priceId && priceId === team) return 'team';
  return null;
}

export async function createCheckout(user, plan) {
  const price = config.stripe.prices[plan];
  if (!price) throw new Error(`No Stripe price configured for plan "${plan}"`);
  const session = await stripe('/checkout/sessions', {
    mode: 'subscription',
    'line_items[0][price]': price,
    'line_items[0][quantity]': '1',
    client_reference_id: String(user.id),
    customer_email: user.email,
    'metadata[plan]': plan,
    'subscription_data[metadata][user_id]': String(user.id),
    allow_promotion_codes: 'true',
    success_url: `${config.publicUrl}/account?upgraded=1`,
    cancel_url: `${config.publicUrl}/pricing`,
  });
  return session.url;
}

export async function createPortal(customerId) {
  const session = await stripe('/billing_portal/sessions', { customer: customerId, return_url: `${config.publicUrl}/account` });
  return session.url;
}

/**
 * Verify a Stripe webhook signature (scheme v1: HMAC-SHA256 over "t.payload").
 * @returns the parsed event, or throws.
 */
export function verifyWebhook(rawBody, header, secret, { toleranceSec = 300, nowSec = Math.floor(Date.now() / 1000) } = {}) {
  const parts = Object.fromEntries(String(header || '').split(',').map((kv) => kv.trim().split('=')).filter((p) => p.length === 2).map(([k, v]) => [k, v]));
  const sigs = String(header || '').split(',').map((kv) => kv.trim()).filter((kv) => kv.startsWith('v1=')).map((kv) => kv.slice(3));
  const t = Number(parts.t);
  if (!t || !sigs.length) throw new Error('Malformed signature header');
  if (Math.abs(nowSec - t) > toleranceSec) throw new Error('Signature timestamp outside tolerance');
  const expected = crypto.createHmac('sha256', secret).update(`${t}.${rawBody}`).digest();
  const match = sigs.some((s) => {
    const got = Buffer.from(s, 'hex');
    return got.length === expected.length && crypto.timingSafeEqual(got, expected);
  });
  if (!match) throw new Error('Signature mismatch');
  return JSON.parse(rawBody);
}

/** Apply a verified Stripe event to the users table. Idempotent per event id. */
export function applyEvent(db, event) {
  if (db.prepare('SELECT 1 FROM stripe_events WHERE id = ?').get(event.id)) return 'duplicate';
  const obj = event.data?.object || {};
  let result = 'ignored';
  if (event.type === 'checkout.session.completed' && obj.mode === 'subscription') {
    const plan = ['pro', 'team'].includes(obj.metadata?.plan) ? obj.metadata.plan : null;
    const userId = Number(obj.client_reference_id);
    if (plan && userId) {
      db.prepare('UPDATE users SET plan = ?, stripe_customer_id = ?, stripe_subscription_id = ? WHERE id = ?').run(plan, obj.customer, obj.subscription, userId);
      result = 'upgraded';
    }
  } else if (event.type === 'customer.subscription.updated' || event.type === 'customer.subscription.deleted') {
    const active = event.type !== 'customer.subscription.deleted' && ['active', 'trialing', 'past_due'].includes(obj.status);
    const plan = active ? planForPrice(obj.items?.data?.[0]?.price?.id) : 'free';
    if (plan) {
      const changes = db.prepare('UPDATE users SET plan = ?, stripe_subscription_id = ? WHERE stripe_customer_id = ?').run(plan, active ? obj.id : null, obj.customer).changes;
      result = changes ? `plan:${plan}` : 'unknown-customer';
    }
  }
  db.prepare('INSERT INTO stripe_events (id, received_at) VALUES (?, ?)').run(event.id, new Date().toISOString());
  return result;
}
