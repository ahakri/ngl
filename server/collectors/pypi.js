// PyPI daily downloads via pypistats.org (sourced from PyPI's public BigQuery
// download logs). `mirrors=false` excludes known mirror traffic. Returns up to
// 180 days of history per package.
import { getJson, HttpError } from './http.js';

/** @returns {Promise<{date:string,value:number}[] | null>} null when the package is unknown */
export async function fetchPypiDaily(pkg) {
  try {
    const body = await getJson(`https://pypistats.org/api/packages/${encodeURIComponent(pkg.toLowerCase())}/overall?mirrors=false`, { minGapMs: 700 });
    return body.data
      .filter((r) => r.category === 'without_mirrors' && r.date)
      .map((r) => ({ date: r.date, value: r.downloads }))
      .sort((a, b) => (a.date < b.date ? -1 : 1));
  } catch (err) {
    if (err instanceof HttpError && err.status === 404) return null;
    throw err;
  }
}
