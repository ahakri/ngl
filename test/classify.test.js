import test from 'node:test';
import assert from 'node:assert/strict';
import { categorize, classify, extract, outcomeOf } from '../server/classify.js';

// Titles below are real agenda items collected from public Legistar portals.
const cat = (title, extra = {}) => categorize({ title, ...extra }).category;

test('entitlements for a private development are projects, with size extracted', () => {
  const title = 'ZON25-00626. "NTT Mesa PH10" 170± acres located at the northeast corner of East Pecos Road and the South Crismon Road alignment. Rezone from Light Industrial with a Planned Area Development Overlay (LI-PAD) to Light Industrial with a new Planned Area Development Overlay (LI-PAD), Council Use Permit and Major Site Plan Modification. This request will allow for an approximately 2,257,581± square foot Data Center development. (District 6). \n\nPlanner: Joshua Grandlienard\nStaff Recommendation: Approval with Conditions';
  const c = classify({ title, status_name: 'Agenda Ready' });
  assert.equal(c.category, 'project');
  assert.equal(c.acres, 170);
  assert.equal(c.square_feet, 2257581);
  assert.equal(c.project_name, 'NTT Mesa PH10');
  assert.equal(c.case_number, 'ZON25-00626');
  assert.equal(c.staff_recommendation, 'Approval with Conditions');
  assert.equal(c.outcome, 'pending');
  assert.equal(cat('PRELIMINARY PLAT FOR COMPASS DATACENTERS PROPOSED ACTION: Recommend approval of the request for a preliminary plat for Compass Datacenters, subject to stipulations.'), 'project');
  assert.equal(cat('Action on a new data center at 1111 Comstock Street'), 'project');
  assert.equal(cat('Preliminary Review of a Major Site Plan Review Application to Construct a Three-Story Data Center, Generator Yards, Substation, Switching Yard, and Related Accessory Structures'), 'project');
});

test('moratoria, bans and code changes are policy, flagged restrictive where they restrict', () => {
  const m = categorize({ title: 'Extension of Moratorium on New Data Centers: Adoption of an Interim Urgency Ordinance Pursuant to California Government Code Section 65858' });
  assert.deepEqual(m, { category: 'policy', restrictive: true });
  // A moratorium that lists the permit types it freezes is still policy, not a project.
  assert.equal(cat('AN ORDINANCE IMPOSING A TEMPORARY MORATORIUM ON REZONING, CONDITIONAL USE PERMITS AND DEVELOPMENT PLAN APPLICATIONS RELATING TO DATA CENTERS'), 'policy');
  const ban = categorize({ title: 'Request approval of a Resolution by the Fulton County Board of Commissioners opposing the provision of tax abatements or other financial incentives by any Development Authority within Fulton County for Data Center Projects' });
  assert.deepEqual(ban, { category: 'policy', restrictive: true });
  const study = categorize({ title: 'Data Centers in Dallas: Preliminary Research [Emily Liu, Director, Planning and Development]' });
  assert.deepEqual(study, { category: 'policy', restrictive: false });
  assert.equal(cat('Request: Text Amendment to the Land Development Code Project Name: Data Centers Applicant: Louisville Metro'), 'policy');
  assert.equal(cat('AN ORDINANCE AMENDING THE LOUISVILLE METRO LAND DEVELOPMENT CODE REGARDING DATA CENTERS (CASE NO. 25-LDC-0014).'), 'policy');
  assert.equal(cat('A Resolution of the Board of Commissioners of DeKalb County, Georgia Urging the Administration to Expand the Definition of Data Centers in the Zoning Ordinance'), 'policy');
});

test('incentives and utility agreements get their own categories', () => {
  assert.equal(cat('Authorize a real property tax abatement agreement with Equinix LLC for the purpose of granting a ten-year abatement of 50 percent of the taxes on the added value'), 'incentive');
  assert.equal(cat('Action on a Substation Agreement with Vantage Data Centers CA31, LLC for Bowers Avenue Junction Substation and Related Budget Amendment'), 'utility');
  assert.equal(cat('Adoption of a Resolution approving a Water Supply Assessment for a data center at 1101 Space Park Drive.'), 'utility');
});

test("a government's own server room is excluded", () => {
  for (const t of [
    'To authorize the Director of Finance and Management, on behalf of the Office of Construction Management, to modify and increase the architectural / engineering services agreement with BBCO Design LLC; for the 2026 Data Center West Facility Upgrades project',
    'Authorize a ten-year cooperative purchasing agreement for data center relocation, operating, and managed services for the Department of Information and Technology Services with Terralogic Solutions, Inc.',
    'Communication from the City Comptroller relating to the audit of Information Technology Management Division Data Center Controls.',
    'Purchase Agreement with SHI Government Solutions Inc. for 1300 Microsoft Windows Server 2019 Client Access Licenses, 110 Microsoft Windows Server 2019 Datacenter Licenses',
    'Authorizing the expenditure of $150,000 from the Capital Improvement Fund for the purpose of purchasing Air Conditioning Units and Replacement of the Uninterrupted Power Supply in the data center',
  ]) assert.equal(cat(t), 'municipal_it', t.slice(0, 60));
});

test('size extraction handles units, ranges and nonsense', () => {
  assert.deepEqual(extract('a 300 MW campus on 1,250.5 acres with 4.2 million sq ft').mw, 300);
  assert.equal(extract('a 300 MW campus on 1,250.5 acres').acres, 1250.5);
  assert.equal(extract('up to 1.2 gigawatts of load').mw, 1200);
  assert.equal(extract('two buildings of 250,000 square feet and 410,000 SF').square_feet, 410000);
  assert.equal(extract('Ordinance 2026 concerning 0 acres').acres, null);
  assert.equal(extract('nothing to see').project_name, null);
});

test('outcomes normalise local status labels and the latest action', () => {
  assert.equal(outcomeOf('Passed'), 'approved');
  assert.equal(outcomeOf('Adopted'), 'approved');
  assert.equal(outcomeOf('Agenda Ready'), 'pending');
  assert.equal(outcomeOf('Failed'), 'denied');
  assert.equal(outcomeOf('Withdrawn'), 'withdrawn');
  assert.equal(outcomeOf('Agenda Ready', [{ action: 'Approved', result: 'Pass' }]), 'approved');
  assert.equal(outcomeOf('In Committee', [{ action: 'Approved' }, { action: 'Continued to a date certain' }]), 'continued');
  assert.equal(outcomeOf('Agenda Ready', [{ action: 'Denied', result: 'Fail' }]), 'denied');
});
