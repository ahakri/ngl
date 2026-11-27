// Polite JSON fetcher shared by all collectors: per-host pacing, timeouts,
// and retry with backoff on 429 / 5xx / network errors.
import { config } from '../config.js';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const lastCall = new Map();

export class HttpError extends Error {
  constructor(status, url) {
    super(`HTTP ${status} for ${url}`);
    this.status = status;
  }
}

/**
 * @param {string} url
 * @param {{ minGapMs?: number, retries?: number, timeoutMs?: number, raw?: boolean }} [opts]
 * @returns {Promise<any>} parsed JSON (or the Response when opts.raw)
 */
export async function getJson(url, opts = {}) {
  const { minGapMs = 250, retries = 4, timeoutMs = 30000, raw = false } = opts;
  const host = new URL(url).host;
  for (let attempt = 0; ; attempt++) {
    const wait = (lastCall.get(host) || 0) + minGapMs - Date.now();
    if (wait > 0) await sleep(wait);
    lastCall.set(host, Date.now());
    let res;
    try {
      res = await fetch(url, {
        headers: { 'user-agent': config.userAgent, accept: 'application/json' },
        signal: AbortSignal.timeout(timeoutMs),
      });
    } catch (err) {
      if (attempt >= retries) throw new Error(`fetch failed for ${url}: ${err.cause?.code || err.message}`);
      await sleep(1000 * 2 ** attempt);
      continue;
    }
    if (res.ok) return raw ? res : res.json();
    const retryable = res.status === 429 || res.status >= 500;
    if (!retryable || attempt >= retries) throw new HttpError(res.status, url);
    const retryAfter = Number(res.headers.get('retry-after'));
    await res.arrayBuffer().catch(() => {});
    await sleep(Number.isFinite(retryAfter) && retryAfter > 0 ? Math.min(retryAfter, 120) * 1000 : 2000 * 2 ** attempt);
  }
}
