// Polite JSON fetcher: per-host pacing, timeouts, retry with backoff on 429 / 5xx / network errors.
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const lastCall = new Map();

export class HttpError extends Error {
  constructor(status, url) {
    super(`HTTP ${status} for ${url}`);
    this.status = status;
  }
}

export async function getJson(url, { minGapMs = 300, retries = 3, timeoutMs = 30000 } = {}) {
  const host = new URL(url).host;
  for (let attempt = 0; ; attempt++) {
    const wait = (lastCall.get(host) || 0) + minGapMs - Date.now();
    if (wait > 0) await sleep(wait);
    lastCall.set(host, Date.now());
    let res;
    try {
      res = await fetch(url, { headers: { 'user-agent': 'siteline-collector/0.1', accept: 'application/json' }, signal: AbortSignal.timeout(timeoutMs) });
    } catch (err) {
      if (attempt >= retries) throw new Error(`fetch failed for ${url}: ${err.cause?.code || err.message}`);
      await sleep(1000 * 2 ** attempt);
      continue;
    }
    if (res.ok) return res.json();
    await res.arrayBuffer().catch(() => {});
    if ((res.status !== 429 && res.status < 500) || attempt >= retries) throw new HttpError(res.status, url);
    await sleep(2000 * 2 ** attempt);
  }
}
