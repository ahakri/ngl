// Legistar Web API (webapi.legistar.com): the official, public, unauthenticated
// API behind many US city and county legislative portals.
import { getJson } from './http.js';

const BASE = 'https://webapi.legistar.com/v1';
// Substrings searched in each item's title and short name.
export const TERMS = ['data center', 'datacenter', 'data centre', 'data processing facilit', 'large load'];

const filter = () => TERMS.flatMap((t) => [`substringof('${t}',MatterTitle)`, `substringof('${t}',MatterName)`]).join(' or ');
const day = (v) => (v ? String(v).slice(0, 10) : null);

/** All matching legislative items for one jurisdiction, optionally only those changed since a UTC timestamp. */
export async function fetchMatters(client, sinceUtc = null) {
  const out = [];
  const where = sinceUtc ? `(${filter()}) and MatterLastModifiedUtc gt datetime'${sinceUtc}'` : filter();
  for (let skip = 0; ; skip += 1000) {
    const qs = new URLSearchParams({ $filter: where, $top: '1000', $skip: String(skip), $orderby: 'MatterId' });
    const page = await getJson(`${BASE}/${client}/matters?${qs}`);
    out.push(...page);
    if (page.length < 1000) break;
  }
  return out.map((m) => ({
    external_id: String(m.MatterId),
    guid: m.MatterGuid,
    file: m.MatterFile || null,
    name: m.MatterName || null,
    title: (m.MatterTitle || m.MatterName || '').replace(/\r/g, '').trim(),
    type_name: m.MatterTypeName || null,
    status_name: m.MatterStatusName || null,
    body_name: m.MatterBodyName || null,
    intro_date: day(m.MatterIntroDate),
    agenda_date: day(m.MatterAgendaDate),
    passed_date: day(m.MatterPassedDate),
    modified_utc: m.MatterLastModifiedUtc || null,
    url: `https://${client}.legistar.com/LegislationDetail.aspx?ID=${m.MatterId}&GUID=${m.MatterGuid}`,
  }));
}

/** Action history of one item: each hearing or vote, oldest first. */
export async function fetchHistory(client, matterId) {
  const rows = await getJson(`${BASE}/${client}/matters/${matterId}/histories`);
  return rows
    .filter((h) => h.MatterHistoryActionDate)
    .map((h) => ({
      external_id: String(h.MatterHistoryId),
      date: day(h.MatterHistoryActionDate),
      body: h.MatterHistoryActionBodyName || null,
      action: h.MatterHistoryActionName || null,
      result: h.MatterHistoryPassedFlagName || null,
      tally: h.MatterHistoryTally || null,
    }))
    .sort((a, b) => (a.date < b.date ? -1 : 1));
}
