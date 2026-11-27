// npm daily downloads from the registry's public downloads API.
import { getJson, HttpError } from './http.js';
import { addDays, today } from '../db.js';

/** @returns {Promise<{date:string,value:number}[] | null>} null when the package is unknown */
export async function fetchNpmDaily(pkg, days = 365) {
  const end = addDays(today(), -1);
  const start = addDays(end, -Math.min(days, 540) + 1); // API caps a range at 18 months
  try {
    // Scoped names keep their slash; only the @ needs no escaping here.
    const body = await getJson(`https://api.npmjs.org/downloads/range/${start}:${end}/${pkg}`, { minGapMs: 300 });
    const pts = (body.downloads || []).map((r) => ({ date: r.day, value: r.downloads }));
    // The newest day is reported as 0 until npm finishes counting it.
    while (pts.length && pts.at(-1).value === 0) pts.pop();
    // Leading zeros are days before the package existed.
    while (pts.length && pts[0].value === 0) pts.shift();
    return pts;
  } catch (err) {
    if (err instanceof HttpError && err.status === 404) return null;
    throw err;
  }
}
