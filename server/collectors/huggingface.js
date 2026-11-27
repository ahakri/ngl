// Hugging Face Hub: snapshot the most-downloaded and the trending models.
// The Hub reports downloads as a trailing-30-day count, so history is built by
// snapshotting daily.
import { getJson } from './http.js';

const FIELDS = ['downloads', 'likes', 'pipeline_tag', 'library_name', 'createdAt', 'trendingScore'];

function nextLink(res) {
  const m = /<([^>]+)>;\s*rel="next"/.exec(res.headers.get('link') || '');
  return m ? m[1] : null;
}

async function page(sort, limit) {
  const out = [];
  const qs = new URLSearchParams({ sort, direction: '-1', limit: String(Math.min(limit, 1000)) });
  for (const f of FIELDS) qs.append('expand[]', f);
  let url = `https://huggingface.co/api/models?${qs}`;
  while (url && out.length < limit) {
    const res = await getJson(url, { raw: true, minGapMs: 800 });
    const rows = await res.json();
    out.push(...rows);
    url = rows.length ? nextLink(res) : null;
  }
  return out.slice(0, limit);
}

/** @returns {Promise<{id,org,task,library,createdAt,downloads,likes,trending}[]>} */
export async function fetchHfModels(limit = 2000) {
  const [top, trending] = [await page('downloads', limit), await page('trendingScore', 200)];
  const seen = new Map();
  for (const m of [...top, ...trending]) {
    if (!m.id || seen.has(m.id)) continue;
    seen.set(m.id, {
      id: m.id,
      org: m.id.includes('/') ? m.id.split('/')[0] : '(legacy)',
      task: m.pipeline_tag || null,
      library: m.library_name || null,
      createdAt: m.createdAt || null,
      downloads: m.downloads || 0,
      likes: m.likes || 0,
      trending: m.trendingScore ?? null,
    });
  }
  return [...seen.values()];
}
