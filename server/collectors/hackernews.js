// Hacker News attention: daily count of stories (and their points) matching a
// phrase, via the public Algolia HN Search API.
import { getJson } from './http.js';

/** @returns {Promise<{date:string, stories:number, points:number}[]>} */
export async function fetchHnDaily(phrase, days = 365) {
  const since = Math.floor(Date.now() / 1000) - days * 86400;
  const byDay = new Map();
  for (let page = 0; page < 5; page++) {
    const qs = new URLSearchParams({
      query: `"${phrase}"`,
      tags: 'story',
      numericFilters: `created_at_i>${since}`,
      hitsPerPage: '1000',
      page: String(page),
      attributesToRetrieve: 'created_at_i,points',
      attributesToHighlight: '',
    });
    const body = await getJson(`https://hn.algolia.com/api/v1/search_by_date?${qs}`, { minGapMs: 400 });
    for (const hit of body.hits || []) {
      const date = new Date(hit.created_at_i * 1000).toISOString().slice(0, 10);
      const row = byDay.get(date) || { date, stories: 0, points: 0 };
      row.stories += 1;
      row.points += hit.points || 0;
      byDay.set(date, row);
    }
    if (page + 1 >= (body.nbPages || 0)) break;
  }
  return [...byDay.values()].sort((a, b) => (a.date < b.date ? -1 : 1));
}
