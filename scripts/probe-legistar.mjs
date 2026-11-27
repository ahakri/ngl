// Coverage tool: check whether candidate Legistar client codes exist, are a
// live government site (not a template), and how many data-centre items they hold.
//
//   node scripts/probe-legistar.mjs mesa "loudoun|Loudoun|Virginia"
//   node scripts/probe-legistar.mjs --file candidates.txt        (one candidate per line)
//
// A candidate is `code` or `code|Place name|State name`. When a place and state
// are given, the tool also counts how many item titles mention each — evidence
// that the code really belongs to that government. One JSON object per line.
import fs from 'node:fs';
import { getJson } from '../server/collectors/http.js';
import { TERMS } from '../server/collectors/legistar.js';

const BASE = 'https://webapi.legistar.com/v1';
const quote = (s) => s.replace(/'/g, "''");
const q = (client, path, params) => getJson(`${BASE}/${client}/${path}?${new URLSearchParams(params)}`, { retries: 0, minGapMs: 350, timeoutMs: 20000 });
const clip = (s, n = 110) => String(s || '').replace(/\s+/g, ' ').trim().slice(0, n);

async function probe(line) {
  const [code, place, state] = line.split('|').map((x) => x.trim());
  const out = { code, place: place || null, state: state || null };
  try {
    out.bodies = (await q(code, 'bodies', { $top: '6', $select: 'BodyName' })).map((b) => b.BodyName);
  } catch {
    return { ...out, exists: false };
  }
  out.exists = true;
  try {
    const recent = await q(code, 'matters', { $top: '3', $orderby: 'MatterIntroDate desc', $filter: "MatterIntroDate lt datetime'2027-06-01'", $select: 'MatterIntroDate,MatterTitle,MatterBodyName' });
    out.latest_intro = recent[0]?.MatterIntroDate?.slice(0, 10) || null;
    out.recent = recent.map((m) => `${m.MatterIntroDate?.slice(0, 10)} [${clip(m.MatterBodyName, 30)}] ${clip(m.MatterTitle)}`);
    const filter = TERMS.flatMap((t) => [`substringof('${t}',MatterTitle)`, `substringof('${t}',MatterName)`]).join(' or ');
    const hits = await q(code, 'matters', { $top: '1000', $filter: filter, $orderby: 'MatterIntroDate desc', $select: 'MatterIntroDate,MatterTitle' });
    out.matches = hits.length;
    out.matches_since_2025 = hits.filter((m) => (m.MatterIntroDate || '') >= '2025-01-01').length;
    out.match_samples = hits.slice(0, 3).map((m) => `${m.MatterIntroDate?.slice(0, 10)} ${clip(m.MatterTitle, 140)}`);
    for (const [key, word] of [['place_mentions', place], ['state_mentions', state]]) {
      if (!word) continue;
      const rows = await q(code, 'matters', { $top: '50', $filter: `substringof('${quote(word)}',MatterTitle)`, $select: 'MatterTitle' });
      out[key] = rows.length; // capped at 50
      if (key === 'place_mentions') out.place_sample = clip(rows[0]?.MatterTitle, 140) || null;
    }
  } catch (err) {
    out.error = err.message;
  }
  return out;
}

const args = process.argv.slice(2);
const fileAt = args.indexOf('--file');
const candidates = (fileAt >= 0 ? fs.readFileSync(args[fileAt + 1], 'utf8').split('\n') : args).map((x) => x.trim()).filter((x) => x && !x.startsWith('#'));
const seen = new Set();
for (const line of candidates) {
  const code = line.split('|')[0].trim().toLowerCase();
  if (seen.has(code)) continue;
  seen.add(code);
  const res = await probe(line.replace(/^[^|]*/, code));
  // Codes that do not exist are only counted, to keep the output readable.
  if (res.exists) console.log(JSON.stringify(res));
  else process.stderr.write('.');
}
process.stderr.write(`\nprobed ${seen.size} codes\n`);
