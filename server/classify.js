// Turns the free text of a legislative item into structured siting data:
// what kind of item it is, how big the project is, and what happened to it.
// Rule-based on purpose: deterministic, auditable, and free to run.

const has = (text, re) => re.test(text);

// A government's own server room, or a contract to run it — not a siting record.
const MUNICIPAL_IT = /\b(information technology|department of (innovation|technology)|\bIT\b|\bITS\b|\bDoIT\b|managed services|colocation services|co-location services|hosting services|disaster recovery|data center (relocation|migration|consolidation|upgrade|facility upgrades?|west facility|maintenance|hvac|ups|generator replacement|cooling (replacement|upgrade))|(city|county|police|911|court|library|airport|school)'?s? (primary |backup |secondary )?data center|uninterruptible power|server (room|refresh|replacement)|network (equipment|switch)|cooperative purchasing|purchasing agreement|software licen[sc]|cybersecurity|emergency communications)\b/i;

const LAND_USE = /\b(rezon\w*|zoning (case|map|change)|zone change|special (use|exception)|conditional use|council use permit|use permit|site plan|planned (area|unit) development|\bPAD\b|\bPUD\b|\bSUP\b|\bCUP\b|\bplat\b|variance|appeal of|mitigated negative declaration|environmental impact report|architectural (committee|review)|waiver of enforcement|annexation|development plan|design review|certificate of appropriateness|comprehensive plan amendment|general plan amendment|minor land division)\b/i;
const POLICY = /\b(moratorium|text amendment|code amendment|amend(ing|ments?)? (to )?(the )?(\w+ ){0,4}(zoning|city|county|municipal|unified development) (code|ordinance)|zoning ordinance|ordinance (amending|to amend)|proposed amendments?|development standards|special permit provisions|policy|policies|legislative package|regulat\w+|task force|study|research|best practice|working group|non-disclosure|resolution (opposing|supporting|urging)|opposing|noise (ordinance|standards)|water use|setback|overlay district|briefing|presentation|discussion|update to council)\b/i;
const INCENTIVE = /\b(tax (abatement|exemption|incentive|increment|rebate)|abatement|economic development (agreement|incentive|grant)|chapter 380|chapter 312|reinvestment zone|enterprise zone|incentive agreement|development authority|payment in lieu|\bPILOT\b|\bGPLET\b|\bTIF\b|industrial revenue bond|foreign trade zone|job creation|financial incentives?)\b/i;
const UTILITY = /\b(water (service|supply|allocation|agreement)|reclaimed water|wastewater|sewer (service|capacity)|substation|transmission line|electric (service|utility|load)|power (purchase|supply|allocation)|large (electrical )?loads?|interconnection|utility (easement|agreement|service)|gas (turbine|generat)|on-?site generation|megawatts?)\b/i;

// Actions that stop or formally oppose development. Deliberately narrow: "restrictions" and "limits" appear in
// ordinary design standards, and a ban on NDAs restricts the city, not the developer.
const RESTRICTIVE = /\b(moratorium|prohibit\w*|ban(ning|s)?|opposing|oppose[sd]?|pause on|cap on)\b/i;
const NOT_RESTRICTIVE = /non-disclosure/i;
// Procurement and upkeep language: what is left over after the siting rules is usually this.
const PROCUREMENT = /\b(purchase orders?|purchas\w+|licen[sc]es?|warranty|maintenance|audit|servers?|storage|backup|bid|vendor|subscription|equipment|racks?|optimization|contract (with|for|no)|agreement with .* for (the )?(provision|purchase|installation))\b/i;

const num = (s) => Number(String(s).replace(/,/g, ''));

/** Largest plausible match of a "<number> <unit>" pattern, or null. */
function largest(text, re, lo, hi) {
  let best = null;
  for (const m of text.matchAll(re)) {
    const v = num(m[1]);
    if (Number.isFinite(v) && v >= lo && v <= hi && (best === null || v > best)) best = v;
  }
  return best;
}

export function extract(text) {
  const acres = largest(text, /(\d[\d,]*(?:\.\d+)?)\s*(?:±|\+\/-|\+\-)?\s*(?:gross |net )?acres?\b/gi, 0.1, 50000);
  const squareFeet = largest(text, /(\d[\d,]*(?:\.\d+)?)\s*(?:±|\+\/-)?\s*(?:gross )?(?:square[- ]f(?:oo|ee)t|sq\.? ?ft\.?|\bSF\b)/gi, 500, 50_000_000);
  let mw = largest(text, /(\d[\d,]*(?:\.\d+)?)\s*-?\s*(?:megawatts?|MW)\b/gi, 0.5, 20000);
  const gw = largest(text, /(\d[\d,]*(?:\.\d+)?)\s*-?\s*(?:gigawatts?|GW)\b/gi, 0.1, 50);
  if (gw !== null && (mw === null || gw * 1000 > mw)) mw = gw * 1000;
  const quoted = /["“]([^"”]{3,70})["”]/.exec(text);
  const caseNo = /\b([A-Z]{1,5}\d{0,2}-?\d{2,4}-\d{2,6}[A-Z]?)\b/.exec(text) || /\b(Z-\d{1,4}-\d{2,4}|[A-Z]{2,4}\s?\d{2}-\d{2,5})\b/.exec(text);
  const rec = /staff recommendation:\s*([^\n.]{3,60})/i.exec(text);
  return {
    acres,
    square_feet: squareFeet,
    mw,
    project_name: quoted ? quoted[1].replace(/[,.]$/, '').trim() : null,
    case_number: caseNo ? caseNo[1] : null,
    staff_recommendation: rec ? rec[1].trim() : null,
  };
}

/**
 * @returns {{category:string, restrictive:boolean}}
 * category: project | policy | incentive | utility | municipal_it | mention
 */
export function categorize(rec) {
  const text = `${rec.name || ''}\n${rec.title || ''}`;
  const typeBody = `${rec.type_name || ''} ${rec.body_name || ''}`;
  const size = extract(text);
  const landUse = has(text, LAND_USE) || /\b(zoning|plat|planning and zoning|board of adjustment|rezon)/i.test(typeBody);
  const builds = /\bdata cent(er|re)s? (development|campus|project|facility|use|building|park)|allow (for )?(an? )?(approximately )?[\d,±\s]*(square f\w+ )?data cent|(construct\w*|develop\w*|conver\w+|expan\w+) [^.]{0,80}data cent|\bnew (\w+[- ]){0,3}data cent(er|re)\b/i.test(text);

  // A moratorium is policy even when it lists the permit types it freezes.
  if (/\bmoratorium\b/i.test(text)) return { category: 'policy', restrictive: true };
  // Changes to the code itself, and resolutions taking a position, are policy even when they mention permit types.
  if (/\b(amend(ing|s)?|amendments? to) [^.]{0,90}\b(code|ordinances)\b|\bresolution\b[^.]{0,160}\b(urging|requesting|opposing|supporting|requiring)\b/i.test(text) && !/\bacres\b/i.test(text)) {
    return { category: 'policy', restrictive: has(text, RESTRICTIVE) && !has(text, NOT_RESTRICTIVE) };
  }
  // A sized or entitled private development beats everything else.
  if ((landUse && (builds || size.acres || size.square_feet)) && !has(text, /text amendment|code amendment|proposed amendments? to/i)) return { category: 'project', restrictive: false };
  if (has(text, MUNICIPAL_IT) && !builds && !has(text, /moratorium|zoning|rezon|tax abatement|special permit/i)) return { category: 'municipal_it', restrictive: false };
  if (has(text, INCENTIVE) && !has(text, /\b(opposing|oppose|prohibit)/i)) return { category: 'incentive', restrictive: false };
  if (has(text, POLICY) || has(text, /\bdata cent(er|re)s\b.*\b(ordinance|standards|requirements)\b/i)) return { category: 'policy', restrictive: has(text, RESTRICTIVE) && !has(text, NOT_RESTRICTIVE) };
  if (has(text, UTILITY)) return { category: /\b(purchas\w+|capital improvement fund|air conditioning)\b/i.test(text) ? 'municipal_it' : 'utility', restrictive: false };
  if (builds) return { category: 'project', restrictive: false };
  if (landUse) return { category: 'project', restrictive: false };
  if (has(text, PROCUREMENT)) return { category: 'municipal_it', restrictive: false };
  // What remains talks about data centres as an industry: reports, hearings, correspondence.
  if (/\bdata cent(er|re)s\b/i.test(text)) return { category: 'policy', restrictive: has(text, RESTRICTIVE) && !has(text, NOT_RESTRICTIVE) };
  return { category: 'mention', restrictive: false };
}

/** Normalise the many local status and vote labels into one outcome. */
export function outcomeOf(statusName, history = []) {
  const last = [...history].reverse().find((h) => h.action || h.result);
  const s = `${statusName || ''} | ${last?.action || ''} | ${last?.result || ''}`.toLowerCase();
  if (/withdraw/.test(s)) return 'withdrawn';
  if (/\b(den(y|ied|ial)|fail(ed)?|rejected|defeated|disapprov|not approved|veto)/.test(s)) return 'denied';
  if (/\b(continu|defer|postpon|tabled|held|hold|remand|carried over)/.test(s)) return 'continued';
  if (/\b(pass(ed)?|adopt(ed)?|approv(ed|al)|enacted|signed|accepted|granted|confirmed|filed|received)\b/.test(s)) return 'approved';
  return 'pending';
}

export function classify(rec, history = []) {
  const text = `${rec.name || ''}\n${rec.title || ''}`;
  return { ...categorize(rec), ...extract(text), outcome: outcomeOf(rec.status_name, history) };
}

export const CATEGORIES = {
  project: 'Project entitlement',
  policy: 'Policy & regulation',
  incentive: 'Incentives',
  utility: 'Power & water',
  mention: 'Other mention',
  municipal_it: 'Government IT (excluded)',
};
export const OUTCOMES = { approved: 'Approved', denied: 'Denied', continued: 'Continued', pending: 'Pending', withdrawn: 'Withdrawn' };
/** Categories that count as siting records everywhere in the product. */
export const SITING = ['project', 'policy', 'incentive', 'utility'];
