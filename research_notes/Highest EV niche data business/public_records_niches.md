# Niche data businesses built on hard-to-assemble public records (US, status as of late Nov 2026)

Researcher caveats (read first):
- Most findings below come from web-search result summaries, not from reading the primary pages in full. Direct fetches of vendor sites were blocked in this session (www.shovels.ai and www.interconnection.fyi did not resolve), so vendor pricing pages were NOT read first-hand. Figures marked "third-party estimate" are modeled or crowd-sourced, not company-reported.
- Several vendors are quote-only; where no price was found this is stated as a gap, not estimated.
- Willingness-to-pay figures for the candidate niches are inferences anchored on competitor prices, not measured demand.

## 1. What are proven examples of this model and their scale/pricing?

### Takeaway
The model is proven across many verticals, with a consistent pattern: funded incumbents sell quote-gated subscriptions in roughly the $2k-$30k+/year range, while a long tail of pay-per-record scrapers (Apify) has commoditized the easy single-state sources at $2-$17 per 1,000 records. The best small-team proof point found is energy-project tracking (Cleanview: $9,000/yr data-center subscription, 1-10 employees).

### Cited Findings

Building permits
- Shovels sells cleaned public-government data on permits, contractors, properties and local development decisions via API, CLI, warehouse delivery and an AI agent; ~178M permits from 2,770+ jurisdictions per a mid-2026 Sacra report (other sources say 130M+/1,800+). — [Sacra](https://sacra.com/c/shovels/)
- Sacra estimates Shovels at ~$3M ARR as of Aug 2026, up from ~$1.5M at end of 2025 (third-party estimate, not company-reported). — [Sacra](https://sacra.com/c/shovels/)
- Shovels funding: CB Insights reports $7.6M over 5 rounds, latest a $5M seed on 17 Jan 2025; Fundz lists different dates/amounts (sources conflict). — [CB Insights](https://www.cbinsights.com/company/shovels/financials); contradicted in detail by [Fundz](https://app.fundz.net/companies/shovels-26f797); seed coverage at [Commercial Observer](https://commercialobserver.com/?p=523692)
- Shovels acquired ReZone in Jan 2026, adding local-government meeting data ("Decisions", ~100 cities at acquisition), moving upstream from permits to rezoning/planning-commission approvals (source is a Sacra AI-generated report). — [Sacra](https://sacra.com/chat/h/7ee041bd-8e7d-45d8-8815-ff1d24000c5c/)
- A third-party Apify permit/contractor scraper charges from $3.00 per 1,000 permit records. — [Apify](https://apify.com/seibs.co/building-permits-intel)

Court records
- UniCourt: pricing not published; Software Advice lists a starting price of $2,250/month (GetApp shows the same figure as per-user; the sites disagree). — [Software Advice](https://www.softwareadvice.com/bi/unicourt-profile/); [GetApp](https://www.getapp.com/all-software/a/unicourt)
- Docket Alarm: aggregator listings conflict ($49/month vs $99 per feature per month). — [Software Advice](https://www.softwareadvice.com/legal/docket-alarm-profile/)
- UniCourt stated in a declaration (FTC submission) that it aggregates court data from ~15 states and has been prevented from accessing court data for certain jurisdictions or blocked from acquiring a complete dataset. — [Declaration of Joshua Blandi](https://law.resource.org/pub/us/case/ftc/Submission%2002/Declaration%20of%20Joshua%20Blandi.pdf)
- Trellis describes itself as mining state trial court data for law firms, covering thousands of courts and millions of cases. — [Trellis blog](https://blog.trellis.law/trellis/ambitious-effort-to-digitize-state-trial-court-records-provides-unprecedented-insight/)

Government procurement
- GovSpend does not publish prices; Vendr reports a median of ~$11,000/year (range ~$8,050-$32,166, 28 purchases; crowd-sourced). — [Vendr](https://www.vendr.com/marketplace/gov-spend)
- GovTribe publishes prices: $1,900 per seat/year (1 seat), $1,600 for 2-3 seats; Pro $2,100. — [GovTribe pricing](https://govtribe.com/pricing)
- Cloverleaf AI (procurement intelligence built on monitoring public meetings) disclosed an $8M seed round; earlier raised $2.8M; pricing not public. — [GovTech](https://www.govtech.com/biz/procurement-firm-cloverleaf-ai-reveals-8m-funding-round); [GovTech (earlier)](https://govtech.com/biz/cloverleaf-ai-raises-2-8m-to-help-gov-tech-suppliers); [G2](https://www.g2.com/products/cloverleaf-ai/pricing)

Energy: interconnection queues, regulatory dockets, data-centre power
- Berkeley Lab's "Queued Up" 2026 edition publishes a free project-level interconnection queue dataset (Excel) compiled from 50+ grid operators, data through end of 2025, file updated May 2026. — [LBNL](https://emp.lbl.gov/queues)
- Interconnection.fyi / datacenter.fyi are free public resources built by GridTracker; the complete dataset (developer names, documents, daily updates) is paid, delivered as monthly CSV or daily Snowflake share; pricing is demo/quote-based. GridTracker is described as the research firm behind the data in LBNL's Queued Up 2025/2026. — [interconnection.fyi get-data](https://www.interconnection.fyi/get-data); [About GridTracker](https://www.interconnection.fyi/about-gridtracker); [Announcing GridTracker](https://newsletter.interconnection.fyi/p/announcing-gridtracker)
- Interconnection.fyi has a data-center directory of 4,093 records across 48 states; its terms prohibit bulk downloading, scraping or redistribution without written consent. — [interconnection.fyi data-center](https://interconnection.fyi/data-center); [terms](https://www.interconnection.fyi/terms)
- Halcyon (founded 2023) raised a $21M Series A in March 2026 led by Energize Capital (~$31.8M total incl. $10.8M seed Apr 2024); it uses ML/LLMs to aggregate documents from all 50 state PUCs, every ISO/RTO and FERC, sells data subscriptions (e.g. a natural gas plant tracker) plus platform access, and offers a free app. — [Axios Pro](https://www.axios.com/pro/climate-deals/2026/03/16/halcyon-funding-21-million); [Business Wire](https://www.businesswire.com/news/home/20260316032633/en/Halcyon-Raises-%2421-Million-Series-A-To-Bring-AI-Powered-Intelligence-to-the-Energy-Industry)
- Cleanview lists a data-center subscription at $9,000/year; it sells a Behind-the-Meter Data Center Tracker following each on-site power project "from its first permit" (turbines, engines, fuel cells, capacity, status). Founder/CEO Michael Thomas (Boulder, CO). Third-party modeled estimate: ~$342k annual revenue, 1-10 employees (low-confidence). — [Cleanview pricing](https://cleanview.co/pricing); [Cleanview BTM tracker](https://cleanview.co/products/behind-the-meter-tracker); [Crunchbase](https://www.crunchbase.com/person/michael-thomas-5); [Prospeo estimate](https://prospeo.io/c/cleanview-revenue)

Local meetings / council minutes
- Startups summarizing/structuring public meetings include Hamlet (city council and planning commission; one profile lists $5M seed / $10M total, inconsistent), Locunity (councils, commissions, school boards), GroundVue (recorded public meetings into structured data), Hello Citizen, DataMission.ai ($1M seed). — [AI Market Watch (Hamlet)](https://www.ai-market-watch.com/company/hamlet); [Locunity profile](https://newsmachines.beehiiv.com/p/how-locunity-covers-local-meetings-nobody-attends); [FedScoop (GroundVue)](https://fedscoop.com/former-federal-technologists-tap-public-meetings-data-new-ai-venture/); [Dealroom (DataMission)](https://dealroom.co/news/133465-datamission-ai-raises-1m-to-bring-ai-decisions-to-local-government/)

Zoning
- Zoneomics lists an API plan at $284/month with call allotments and overage, plus custom tiers; covers USA and Canada. — [Zoneomics API pricing](https://www.zoneomics.com/pricing/zoning-data-apis)
- National Zoning Atlas is a free public resource (launched early 2024); Regrid launched a zoning product. — [dBusiness](https://www.dbusiness.com/daily-news/regrid-in-detroit-launches-geospatial-product-to-enhance-u-s-zoning-data/)

Insurance rate filings (SERFF)
- S&P Global sells "SNL Insurance Product Filings" extracted from SERFF filings (rate changes, proposals, regulator disposition), with API access to SERFF PDFs. — [S&P Global Marketplace](https://www.marketplace.spglobal.com/en/datasets/snl-insurance-product-filings-(1733129635))
- Akur8 Discover ingests millions of SERFF filings with NLP; rate, form and rule filing data updated biweekly; no public pricing (demo). — [Akur8 Discover](https://akur8.com/pricing/discover)
- A community Apify actor scrapes SERFF on pay-per-usage pricing. — [Apify](https://apify.com/fortuitous_pirate/serff-insurance-scraper)

Healthcare price transparency
- Turquoise Health tracks 219 payers' file locations and estimates it ingests up to 300 TB of data per month; Serif Health ingests 200+ commercial payers' in-network MRFs monthly (sales-contact pricing); Payerset (31 unique customers incl. nine health systems at time of coverage) now appears in an IQVIA 2026 fact sheet. — [Turquoise blog](https://turquoise.health/resources/blog/introducing-payer-transparency-scores); [Serif Health](https://www.serifhealth.com/platform/data/payer-transparency-data); [Fierce Healthcare](https://www.fiercehealthcare.com/ai-and-machine-learning/payerset-launches-ai-powered-research-assistant-turn-price-transparency); [IQVIA fact sheet](https://www.iqvia.com/-/media/iqvia/pdfs/us/fact-sheet/2026/iqvia-payerset-data-solutions-fact-sheet-2026.pdf)

Health inspections
- Hazel Analytics collects public data from thousands of health departments into a standardized format; claims to serve nearly half of the 100 largest food-service/retail brands; supplies hygiene data on ~700,000 Yelp pages across 48 states; pricing unpublished. — [TechCrunch](https://techcrunch.com/2022/03/31/yelp-restaurant-health-ratings-in-partnership-with-food-tech-startup-hazel-analytics); [GeekWire](https://www.geekwire.com/2022/data-startup-expands-partnership-with-yelp-to-provide-health-ratings-for-restaurants/); [G2](https://www.g2.com/products/hazel-analytics/pricing)

Import/export bills of lading
- ImportGenius: 300M+ US import bills of lading from CBP vessel manifests (2006-present); Global Enterprise tier from $1,999/month; Business/Enterprise are annual plans. — [ImportGenius pricing](https://importgenius.com/pricing); [ImportGenius BoL database](https://www.importgenius.com/features/bill-of-lading-database)
- Panjiva (S&P Global) has no public list price; a competitor page claims it starts at $159/month billed yearly (competitor's claim). — [ImportGenius comparison](https://www.importgenius.com/comparison/panjiva)
- ImportYeti offers the data free to view, obtained via a FOIA request to US Customs (from Jan 2015). — [Bellingcat toolkit](https://bellingcat.gitbook.io/toolkit/more/all-tools/importyeti)

Licences (liquor, cannabis, business)
- Liquor/new-business-licence lead feeds are sold per record on Apify: from $1.80/1,000 (multi-city new licences), $3.00/1,000 (7-state liquor monitor), $4.00/1,000 (CA/NY/TX), up to $17/1,000 (owners and addresses). — [Apify: 7-state monitor](https://apify.com/wallman_3rd/liquor-license-monitor); [Apify: filingradar](https://apify.com/filingradar/us-liquor-license-filings); [Apify: owners scraper](https://apify.com/scrapers_lat/usa-liquor-licenses-scraper)
- Cannabiz Media's licence database was priced at $3,600/year in a 2016 press release (old; current price not found). — [PRWeb](https://www.prweb.com/releases/cannabiz_media_launches_the_most_comprehensive_marijuana_licensing_database_and_directory_detailed_data_on_over_10_000_marijuana_licenses_updated_daily/prweb13847152.htm); [Cannabiz pricing page](https://cannabiz.media/pricing)

UCC filings and liens
- States sell or publish UCC data directly: Texas daily updates at $65/day (data), $90/day (data+images), master unload $1,150; Connecticut's lien dataset is free on its open-data portal with API; Kentucky generates a daily new-filings file and monthly full listing; West Virginia publishes new UCC filings weekly; Minnesota sells active liens plus two years lapsed. — [Texas SOS](https://www.sos.state.tx.us/ucc/bulk-order.shtml); [Connecticut](https://business.ct.gov/Knowledge-Base/Article/Sots/Bulk-Data-and-Images); [Kentucky SOS](https://sos.ky.gov/bus/Pages/Bulk-Data-Service.aspx); [West Virginia](https://apps.wv.gov/SOS/BulkData/Forms/FileDescriptions.aspx); [Minnesota SOS](https://sos.mn.gov/business-liens/business-liens-data/ucc-data-available-for-purchase/)
- An Apify UCC/lien actor (CT, CO, NY, OR open-data APIs) charges from $2.40 per 1,000 filings. — [Apify](https://apify.com/northbell/ucc-filings)

### Inferences
- Two-tier market structure: (1) VC-backed/enterprise incumbents with quote-only pricing in the low-thousands to tens-of-thousands per year; (2) per-record commodity scrapers. The gap between them (a few hundred dollars a month, narrow vertical, fresh alerts, self-serve) recurs in most categories.
- Value accrues to assembly breadth plus normalization plus entity resolution, not to any single source; single-state/single-portal feeds are already commoditized on Apify at a few dollars per thousand rows.
- Cleanview and GridTracker suggest small teams can win in energy by choosing a narrow object (a project, a queue position) and tracking it across many fragmented sources; both ended up pricing at enterprise-ish levels.

### Gaps
- No first-hand read of Shovels, GridTracker, Sweetspot, Trellis, Hazel, Turquoise, Serif, Akur8 or S&P pricing; all are quote-gated or the pages were unreachable. Sweetspot pricing/funding: nothing reliable found ([G2 page has no figure](https://www.g2.com/products/sweetspot-sweetspot/pricing)).
- No founder-interview (Indie Hackers/podcast) evidence found for a solo-founder public-records data business with disclosed MRR; the one search attempt returned irrelevant results.
- Not researched in this pass (no sourced findings): FiscalNote/Quorum/Plural (legislation), FDA/EPA/OSHA enforcement products, SEC-filing derivatives, FCC/FAA filings, public pension and university procurement, BuildZoom/ATTOM, GovWin pricing.

## 2. Which niches are saturated and which are underserved or only served at enterprise price points?

### Takeaway
Saturated or structurally hard for a solo founder: building permits, federal/SLED procurement, bills of lading, hospital/payer price transparency, restaurant health inspections, single-state licence lead feeds. Served mainly at enterprise/quote-only price points with visible room for a cheaper or narrower product: SERFF insurance filings, energy/data-centre siting records (queues, large-load dockets, air permits, local zoning fights), state PUC dockets, and vertical-specific local-meeting intelligence.

### Cited Findings
- Building permits: Shovels has 2,770+ jurisdictions and is expanding upstream into meeting data; per-record scrapers undercut at $3/1,000. — [Sacra](https://sacra.com/c/shovels/); [Apify](https://apify.com/seibs.co/building-permits-intel)
- Procurement: multiple players with published low-end pricing (GovTribe $1,900/seat/yr) through enterprise (GovSpend median ~$11k/yr) plus newly funded AI entrants (Cloverleaf $8M). — [GovTribe](https://govtribe.com/pricing); [Vendr](https://www.vendr.com/marketplace/gov-spend); [GovTech](https://www.govtech.com/biz/procurement-firm-cloverleaf-ai-reveals-8m-funding-round)
- Bills of lading: a free product (ImportYeti) coexists with $1,999/month enterprise tiers. — [Bellingcat toolkit](https://bellingcat.gitbook.io/toolkit/more/all-tools/importyeti); [ImportGenius pricing](https://importgenius.com/pricing)
- Price transparency: data volume is extreme (up to 300 TB/month ingested by Turquoise) and the category has consolidated toward large vendors (Payerset inside IQVIA materials). — [Turquoise blog](https://turquoise.health/resources/blog/introducing-payer-transparency-scores); [IQVIA](https://www.iqvia.com/-/media/iqvia/pdfs/us/fact-sheet/2026/iqvia-payerset-data-solutions-fact-sheet-2026.pdf)
- Liquor/business licence leads: at least ten competing Apify actors priced $1.80-$17 per 1,000 records. — [Apify example](https://apify.com/wallman_3rd/liquor-license-monitor); [Apify example](https://apify.com/filingradar/us-liquor-license-filings)
- Health inspections: one incumbent claims about half of the top-100 food brands and exclusive Yelp supply. — [GeekWire](https://www.geekwire.com/2022/data-startup-expands-partnership-with-yelp-to-provide-health-ratings-for-restaurants/)
- SERFF: only enterprise vendors (S&P, Akur8 by demo) plus one community scraper; S&P's product is described in one commentary as lacking real-time alerting. — [S&P Marketplace](https://www.marketplace.spglobal.com/en/datasets/snl-insurance-product-filings-(1733129635)); [Akur8](https://akur8.com/pricing/discover); [Apify](https://apify.com/fortuitous_pirate/serff-insurance-scraper)
- Energy siting: vendors exist but price by quote or at $9,000/yr for a single tracker; a search found no single national dataset consolidating large-load interconnection requests across utilities and PUC dockets (ERCOT publishes large-load queue status only inside TAC report PDFs). — [Cleanview pricing](https://cleanview.co/pricing); [ERCOT March 2026 TAC report](https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf); [interconnection.fyi get-data](https://www.interconnection.fyi/get-data)
- Court records: even the best-known aggregator reports only ~15 states and being blocked by courts; entry price ~$2,250/month. — [Blandi declaration](https://law.resource.org/pub/us/case/ftc/Submission%2002/Declaration%20of%20Joshua%20Blandi.pdf); [Software Advice](https://www.softwareadvice.com/bi/unicourt-profile/)
- Local meetings: several funded startups, but the largest structured product found (Shovels/ReZone "Decisions") covered only ~100 cities at acquisition in Jan 2026. — [Sacra](https://sacra.com/chat/h/7ee041bd-8e7d-45d8-8815-ff1d24000c5c/)

### Inferences
- Saturated (avoid): permits (national), procurement, bills of lading, restaurant inspections, generic licence leads, generic price-transparency.
- Enterprise-only with a visible low end missing: SERFF filings; energy/data-centre siting; PUC dockets (Halcyon's free app compresses the low end here, so only a narrow extracted dataset, not search, is defensible).
- Thin coverage relative to the universe: local meetings (~100 cities vs. tens of thousands of local bodies); state trial courts (~15 states), though courts carry the heaviest PII/access risk.
- "Underserved" here means "no cheap, self-serve, narrow product found by search"; that is absence of evidence, not proof of demand.

### Gaps
- Could not verify the "no real-time alerting" claim about S&P's SERFF product at a primary source; it came from a search summary of secondary commentary.
- No data on churn, customer counts or revenue for the meeting-intelligence startups.

## 3. Which public-record sources are newly available or newly valuable in 2025-2026?

### Takeaway
The clearest 2025-2026 demand shock is data-centre and power siting: large-load tariffs and dockets, local moratoria and zoning fights, and air permits for on-site gas generation all generate new fragmented public records that buyers are already paying for. Price-transparency rules also tightened in 2026 but favour large-scale processors. PFAS (TSCA) reporting data is delayed to 2027 and state AI registries have not yet produced substantial public datasets.

### Cited Findings

Data centres, large loads and energy
- State regulators approved 29 large-load tariffs in 2025 (EPRI presentation citing Utility Dive); most regions took some action on large loads in 2025, with FERC/PJM co-location proceedings ongoing. — [EPRI](https://restservice.epri.com/publicattachment/98541); [McGuireWoods 2026 regulatory outlook](https://www.mcguirewoods.com/client-resources/alerts/2026/2/2026-regulatory-outlook-key-federal-and-state-proceedings-shaping-data-center-electric-supply/)
- LBNL published a large-load review (Sept 2026) and New Mexico's PRC published a Large Load Policy & Technical Analysis Survey (Aug 2026). — [LBNL large-load review](https://eta-publications.lbl.gov/sites/default/files/2026-08/lbnl_lllreview_september_2026.pdf); [NM PRC survey](https://www.prc.nm.gov/wp-content/uploads/2026/08/Large-Load-Policy-Technical-Analysis-Survey-v-3.0.pdf)
- Active projects in data-centre load-growth zones wait 3-4 years in PJM and ERCOT queues. — [Carbon Direct](https://www.carbon-direct.com/research-and-reports/ai-meets-the-grid-interconnection-queue-analysis-in-pjm-and-ercot)
- Local moratoria: a U.S. Data Center Moratorium Tracker counted 127 jurisdictions with moratoriums besides New York State; New York announced the first state-level pause (July 2026); nearly 40 Georgia local governments approved some form of moratorium; the National League of Cities runs a Data Center Local Action Tracker. — [Route Fifty, Aug 2026](https://www.route-fifty.com/artificial-intelligence/2026/08/many-localities-have-tried-data-center-moratoriums-tracker-finds/415696/); [NCSL](https://www.ncsl.org/resources/details/new-york-hits-pause-on-data-centers-will-other-states-follow)
- At least 75 US data-centre projects worth ~$130B were blocked or delayed in Q1 2026 (citing Data Center Watch). — [Network World](https://www.networkworld.com/article/4200222/data-center-energy-constraints-and-moratoriums-are-mounting-expect-to-see-stalled-ai-projects.html)
- On-site power: up to 138 GW of behind-the-meter gas capacity announced by developers (Sierra Club, Nov 2026, citing an Environmental Integrity Project database); Floodlight (July 2026) identified thousands of data-centre on-site power sources approved through minor permits without public input; a Texas Tribune analysis used Clean Air Act construction-permit applications. — [Sierra Club report](https://www.sierraclub.org/sites/default/files/2026-11/artificialintegrity_report_pdf.pdf); [Texas Tribune](https://www.texastribune.org/2026/07/09/texas-data-centers-ai-power-plants-pollution-state-permits/)
- A January 2026 EPA rule significantly reduced permit obligations for certain turbines used for data centres; air permits for data centres are a contested topic ahead of a further EPA rule revision. — [JD Supra](https://www.jdsupra.com/legalnews/epa-s-new-turbine-rules-provide-air-9433112/); [S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/083126-air-permits-for-data-centers-heated-topic-ahead-of-epa-rule-revision)
- Utilities' AI use is itself becoming a docketed subject: Arizona opened Docket AU-00000A-26-0060 (March 2026); New York is moving to require utility AI reporting; Connecticut's AG asked PURA for a review (Oct 2026). — [Arizona Corporation Commission](https://azcc.gov/news/home/2026/03/27/commissioner-lea-m%C3%A1rquez-peterson-opens-formal-inquiry-into-potential-use-of-artificial-intelligence-in-utilities--operations); [Bloomberg Government](https://news.bgov.com/bloomberg-government-news/cyber-fears-drive-new-yorks-push-to-audit-utilities-use-of-ai); [MLex](https://www.mlex.com/mlex/articles/2537427)

Price transparency
- CMS replaced the estimated-allowed-amount field with new allowed-amount elements (incl. median) effective 1 Jan 2026, with enforcement from 1 Apr 2026. — [CMS fact sheet](https://www.cms.gov/newsroom/fact-sheets/cy-2026-opps-ambulatory-surgical-center-final-rule-hospital-price-transparency-policy-changes); [Penn State PORH](https://www.porh.psu.edu/hospital-price-transparency-enforcement-of-2026-requirements-starts-april-1/)
- A proposed Transparency in Coverage rule would have insurers publish one rate per provider network rather than per plan, which could ease matching payer and hospital files. — [HFMA](https://www.hfma.org/price-transparency/transparency-in-coverage-proposed-rule-tic-files/); [DWT](https://www.dwt.com/insights/2026/10/new-payor-transparency-rules-hospital-impact)
- AHA argues the files lack the algorithms plans use to turn rates into actual payments. — [AHA fact sheet, June 2026](https://www.aha.org/fact-sheets/2026-06-05-fact-sheet-hospital-price-transparency-current-landscape-and-better-path-forward)

PFAS / environmental
- EPA's April 2026 final rule moved the start of the TSCA 8(a)(7) PFAS reporting period to 31 Jan 2027 or 60 days after a forthcoming scope revision, whichever is earlier; EPA proposed narrowing scope in Nov 2025. — [Federal Register, 13 Apr 2026](https://www.govinfo.gov/content/pkg/FR-2026-04-13/html/2026-07062.htm); [Faegre Drinker](https://www.faegredrinker.com/en/insights/publications/2026/4/epa-extends-pfas-reporting-start-date-under-tsca-section-8a7)

State privacy / AI registries
- California's Data Broker Registry reached 581 registered brokers (June 2026); brokers had to begin processing DROP deletion requests from 1 Aug 2026; first enforcement actions announced Aug 2026. — [CalPrivacy](https://privacy.ca.gov/2026/06/privacy-momentum-builds-300000-californians-sign-up-for-drop-as-registered-data-brokers-hit-a-record-high/); [Governor of California](https://www.gov.ca.gov/2026/08/13/icymi-california-takes-historic-action-against-data-brokers/)
- Colorado's AI Act effective date was delayed to 30 June 2026 by SB25B-004 (Aug 2025), with further changes anticipated. — [Greenberg Traurig](https://www.gtlaw.com/en/insights/2025/9/colorado-delays-comprehensive-ai-law-with-further-changes-anticipated)

Insurance filings
- NAIC is modernizing SERFF (April 2026 materials mention API integrations among enhancements). — [NAIC SERFF modernization, Apr 2026](https://content.naic.org/sites/default/files/serff-modernization-lhca-april-2026.pdf)

Zoning / local decisions
- Shovels' Jan 2026 ReZone acquisition is market evidence that pre-permit signals (rezoning, environmental review, planning-commission approvals) are now considered valuable. — [Sacra](https://sacra.com/chat/h/7ee041bd-8e7d-45d8-8815-ff1d24000c5c/)

### Inferences
- The data-centre boom has made three previously sleepy record types commercially valuable at once: (a) state PUC large-load tariff and special-contract dockets, (b) state air-agency minor-source/construction permits, (c) county/municipal zoning, moratorium and hearing records. All three are public, document-heavy and scattered across 50 state agencies and thousands of local bodies.
- The existing free trackers (NLC, moratorium tracker, Data Center Watch, EIP database) are advocacy/association products; they prove interest but are not built as commercial, structured, alerting feeds.
- PFAS/TSCA data is a "watch" item, not a 2026 opportunity; nothing will be filed before 2027 and public release terms are unknown.
- State AI/privacy registries currently yield small datasets (hundreds of rows) with limited standalone value.

### Gaps
- Status of the Colorado AI Act after the 2026 session was not confirmed; California AB 2013 training-data disclosures and any other AI-filing registries were not found by search.
- Tariff/trade-change record sources (e.g. exclusion requests, CBP rulings) and local zoning-reform datasets were not researched.
- No source found on whether TSCA 8(a)(7) submissions will be public or on PFAS drinking-water monitoring data vendors.

## 4. For the most promising underserved niches: buyers, price, collection method, difficulty, legal constraints

### Takeaway
Seven candidates fit a solo, software-only founder; the strongest by combination of fresh demand, weak low-end competition and tractable collection are (1) data-centre siting records at the local/state level, (2) SERFF rate-filing intelligence for a narrow insurance line, and (3) vertical-specific local-meeting alerts. Buyer/price statements below are inferences anchored on cited competitor prices unless a source is given.

### Cited Findings

Candidate A: Data-centre local approvals and opposition (zoning hearings, moratoria, conditional-use permits, tax-abatement votes)
- Demand evidence: 127+ local moratoria tracked; ~75 projects/~$130B blocked or delayed in Q1 2026; litigation over county moratoria (Imperial County CA, Chatham County NC). — [Route Fifty](https://www.route-fifty.com/artificial-intelligence/2026/08/many-localities-have-tried-data-center-moratoriums-tracker-finds/415696/); [Network World](https://www.networkworld.com/article/4200222/data-center-energy-constraints-and-moratoriums-are-mounting-expect-to-see-stalled-ai-projects.html)
- Competitors: free association/advocacy trackers (NLC, moratorium tracker); datacenter.fyi (4,093 records, paid full data by quote); Cleanview at $9,000/yr; Shovels Decisions (~100 cities). — [interconnection.fyi data-center](https://interconnection.fyi/data-center); [Cleanview pricing](https://cleanview.co/pricing); [Sacra](https://sacra.com/chat/h/7ee041bd-8e7d-45d8-8815-ff1d24000c5c/)
- Collection: local agenda/minutes portals and meeting video; no single source exists. — [Route Fifty](https://www.route-fifty.com/artificial-intelligence/2026/08/many-localities-have-tried-data-center-moratoriums-tracker-finds/415696/)

Candidate B: State air permits for on-site/behind-the-meter generation (and minor-source permits generally)
- Demand evidence: 138 GW of BTM gas announced; thousands of on-site sources approved via minor permits with no public notice, i.e. visible only in agency permit systems. — [Sierra Club report](https://www.sierraclub.org/sites/default/files/2026-11/artificialintegrity_report_pdf.pdf); [Texas Tribune](https://www.texastribune.org/2026/07/09/texas-data-centers-ai-power-plants-pollution-state-permits/)
- Competitors: Cleanview Behind-the-Meter tracker; Environmental Integrity Project database; S&P coverage. No consolidated government database found. — [Cleanview BTM tracker](https://cleanview.co/products/behind-the-meter-tracker); [S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/091626-air-pollution-from-data-center-power-projects-is-a-rising-concern-amid-build-out)
- Collection: each state environmental agency's permit portal (e.g. TCEQ in Texas). — [Texas Tribune](https://www.texastribune.org/2026/07/09/texas-data-centers-ai-power-plants-pollution-state-permits/)

Candidate C: Large-load tariffs, special contracts and large-load queues from state PUC dockets and ISO reports
- Demand evidence: 29 large-load tariffs approved in 2025; no consolidated national large-load dataset found; ERCOT large-load queue data sits in TAC report PDFs. — [EPRI](https://restservice.epri.com/publicattachment/98541); [ERCOT TAC report](https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf)
- Competitors: Halcyon (all 50 PUCs, free app plus paid data subscriptions, $31.8M raised); GridTracker; S&P. — [Business Wire](https://www.businesswire.com/news/home/20260316032633/en/Halcyon-Raises-%2421-Million-Series-A-To-Bring-AI-Powered-Intelligence-to-the-Energy-Industry); [interconnection.fyi get-data](https://www.interconnection.fyi/get-data)
- Collection: state PUC e-filing systems; e.g. California PUC publishes weekly "New Filings" lists with proceeding number, date and summary. — [CPUC new filings](https://www.cpuc.ca.gov/news-and-updates/all-news/new-filings---week-of-november-9-13-2026)

Candidate D: SERFF insurance rate/rule/form filings for one narrow line (structured rate-change and rating-factor data plus alerts)
- Demand/competitors: S&P SNL Insurance Product Filings and Akur8 Discover (enterprise, quote); Milliman has published an LLM method for analysing product filings; one Apify scraper. — [S&P Marketplace](https://www.marketplace.spglobal.com/en/datasets/snl-insurance-product-filings-(1733129635)); [Akur8](https://akur8.com/pricing/discover); [Milliman](https://www.milliman.com/en/insight/analyzing-insurance-product-filings-artificial-intelligence-llm); [Apify](https://apify.com/fortuitous_pirate/serff-insurance-scraper)
- Collection: SERFF Filing Access is the NAIC's public portal to rate and form filings (PDF-heavy); some states also run their own portals (e.g. Arkansas rate-change portal, California viewing room). — [NAIC SERFF](https://content.naic.org/industry/serff); [Arkansas portal](https://portal.insurance.arkansas.gov/complianceratechangespublic/compliance-rate-changes/index); [California DOI](https://www.insurance.ca.gov/0250-insurers/0800-rate-filings/0050-viewing-room)
- Legal: the SERFF licence agreement (written for filers) bars reverse engineering and interfering with SERFF operations; NAIC application terms restrict use to authorized users; programmatic access (SERFF Integration Services) is a paid licence for companies; an apis.io profile says NAIC has no self-serve API and licenses bulk data by contract (unverified secondary source). No explicit Filing Access anti-scraping clause was found, and none was ruled out. — [SERFF licence agreement](https://serff.com/documents/implementation_standard_serff_license_agreement.pdf); [NAIC terms](https://content.naic.org/index.php/application/terms-conditions); [apis.io](https://apis.io/providers/naic/)
- NAIC advice to researchers stresses asking vendors what transformations they applied (provenance matters to buyers). — [NAIC CIPR appendix](https://content.naic.org/sites/default/files/cipr-report-appendix-advice-to-researchers.pdf)

Candidate E: Vertical-specific local-meeting intelligence (planning commissions, councils, school boards) for one buyer type
- Demand/competitors: Cloverleaf ($8M seed) sells to government vendors; Hamlet, Locunity, GroundVue, Shovels Decisions (~100 cities). — [GovTech](https://www.govtech.com/biz/procurement-firm-cloverleaf-ai-reveals-8m-funding-round); [FedScoop](https://fedscoop.com/former-federal-technologists-tap-public-meetings-data-new-ai-venture/); [Sacra](https://sacra.com/chat/h/7ee041bd-8e7d-45d8-8815-ff1d24000c5c/)
- Collection cost: an INFORMS 2026 tutorial converted meeting-transcript PDFs to structured JSON at ~$0.0018 per page (gpt-4.1-mini pricing). — [INFORMS](https://pubsonline.informs.org/doi/full/10.1287/inte.2026.0314)

Candidate F: UCC new-filing feeds normalized across states for a niche lender type
- Collection: mixed free and paid state sources (CT free API; KY daily file; WV weekly; TX $65/day or $1,150 master; MN paid). — [Texas SOS](https://www.sos.state.tx.us/ucc/bulk-order.shtml); [Connecticut](https://business.ct.gov/Knowledge-Base/Article/Sots/Bulk-Data-and-Images); [Kentucky SOS](https://sos.ky.gov/bus/Pages/Bulk-Data-Service.aspx)
- Competitors at the low end: Apify actor from $2.40/1,000 filings. — [Apify](https://apify.com/northbell/ucc-filings)

Candidate G: Narrow slice of hospital price-transparency files (one specialty/region)
- Feasibility: 90.3% of hospital files reportedly meet the CMS 3.0 standard format (vendor-reported), which lowers parsing effort for hospital files; payer TiC files remain enormous. — [Business Wire, July 2026](https://www.businesswire.com/news/home/20260714227982/en/); [Turquoise blog](https://turquoise.health/resources/blog/introducing-payer-transparency-scores)

Cross-cutting legal findings
- Federal data is generally free of domestic copyright restrictions; state/local portals can impose different licences, authentication and restrictions, and public visibility is not blanket permission to scrape. — [C4ADS tech bulletin, June 2026](https://c4ads.org/tech-bulletin/to-scrape-or-not-to-scrape/)
- Some state/local record offices impose conditions such as no commercial use or no resale (GAO survey, 2008; shows such limits exist, not that they are universal). — [GAO](https://files.gao.gov/special.pubs/gao-08-1004sp/08-1004sp6.html)
- Court data carries specific risk: NCSC notes harms from scraped records being misused in background checks; UniCourt was sued in June 2025 (N.D./C.D. Cal. federal court) alleging misuse of personal data from court records for targeted advertising under California's right-of-publicity statute and Washington's Personality Rights Act. — [NCSC](https://ncsc.org/information-and-resources/trending-topics/trending-topics-landing-pg/tech-series-whats-web-scraping); [Milberg](https://milberg.com/news/unicourt-privacy-lawsuit/)
- Aggregators themselves restrict reuse: interconnection.fyi's terms prohibit scraping/redistribution, so a new entrant must collect from primary government/utility sources. — [interconnection.fyi terms](https://www.interconnection.fyi/terms)

### Inferences
Assessment table (all cells are researcher inference from the cited findings above; prices are anchored on competitor prices, not tested):

| Candidate | Likely buyers | Plausible price point | Collection | Difficulty | Main legal/ToS risk |
|---|---|---|---|---|---|
| A. Data-centre local approvals/opposition | Developers, site-selection consultants, land brokers, utilities, infrastructure investors, equipment vendors, law firms | $200-$750/mo self-serve, below Cleanview's $9k/yr | Scrape agenda portals + LLM classify; start with highest-activity states (VA, GA, TX, AZ, OH) | Medium: long tail of portals, but only a few hundred active jurisdictions matter | Low: business/government records; avoid republishing individual commenters' personal details |
| B. State air permits for on-site generation | Same as A plus turbine/engine OEMs, EPCs, environmental consultants, NGOs, journalists | $300-$1,000/mo | 50 state agency portals; PDFs of applications | Medium-high: heterogeneous portals, entity matching to data-centre projects | Low; state portal terms vary |
| C. Large-load tariffs/special contracts/queues | Developers, utilities, consultants, hedge funds, energy lawyers | $300-$1,000/mo for an extracted table (not search) | PUC e-filing systems, ISO PDF reports | Medium: 50 docket systems, but Halcyon already indexes them and offers a free app | Low; strongest competitive risk rather than legal risk |
| D. SERFF filings for one line | Regional carriers, MGAs, insurtechs, reinsurance analysts, independent agencies, consultants | $300-$1,500/mo vs enterprise S&P/Akur8 | SERFF Filing Access + state portals; LLM extraction from PDFs | Medium-high: large PDFs, actuarial tables | Medium: NAIC terms unclear for automated public access; needs a careful read before building |
| E. Vertical meeting alerts | Depends on vertical: e.g. developers/land-use attorneys, K-12 vendors, telecom/tower or solar siting teams | $100-$500/mo per region | Agenda/minutes PDFs, video transcripts; cents per document | Medium: portal long tail; funded competitors expanding | Low |
| F. UCC feeds | Equipment finance, factoring/MCA lenders, credit analysts | $100-$500/mo | State bulk files/APIs, some paid | Low-medium | Medium: lead-gen outreach rules; sole-proprietor debtors are individuals (PII), which edges toward the excluded personal-data category; per-state licence terms unverified |
| G. Price-transparency slice | Independent practices, ASCs, benefits consultants, small TPAs | $200-$1,000/mo | CMS-standard hospital MRFs (bulk download) | High compute/storage for payer files; moderate for hospital-only | Low |

- Ranking for a solo founder (inference): A and B together (one "data-centre siting records" product) > D > E (only with a sharply chosen vertical) > C > F > G. A/B have the freshest demand and the least structured supply; D has the clearest price umbrella but the least clear terms-of-use position; C faces a well-funded competitor with a free tier.
- Timing risk for A/B/C: demand depends on the data-centre build-out continuing and on policy churn (EPA turbine rule changes reduce some permit obligations, which also removes some records).
- None of A-E requires paid proprietary licences, field staff or FOIA to start; F partly requires buying state files (e.g. Texas), which is cheap but not free.

### Gaps
- No direct evidence of what buyers in A-E would pay; no interviews, job postings or RFPs were gathered. Prices in the table are anchored only on competitor list/estimated prices.
- Did not read the actual SERFF Filing Access terms of use, robots.txt or the reported NAIC llms.txt; legal position for Candidate D is unresolved.
- Did not verify per-state commercial-use or resale restrictions for UCC bulk data or for state air-permit portals.
- Could not confirm Cleanview's or GridTracker's product scope first-hand (sites not fetched); they may already cover more of A-C than the search summaries show.
- CBP vessel-manifest confidentiality rules, FCRA/DPPA specifics, and state-by-state public-records commercial-use statutes were not researched in depth.

## 5. Does LLM-based extraction newly make datasets feasible for one person?

### Takeaway
Yes on cost, with caveats on accuracy: published 2026 evidence puts LLM extraction of meeting PDFs at roughly $0.002 per page, and incumbents (Halcyon, Akur8, Milliman, Shovels/ReZone, Cloverleaf) are all visibly building on LLM extraction of public filings. The binding constraints for a solo founder are now portal crawling/maintenance and quality assurance on tables and scans, not extraction cost.

### Cited Findings
- An INFORMS (2026) tutorial converted 10 meeting-transcript PDFs to analysis-ready JSON for ~$3.50, a unit cost of ~$0.0018 per page (gpt-4.1-mini pricing at the time); it flags inconsistent layouts, embedded headers/footers and poor digitization as complications. — [INFORMS Journal on Applied Analytics](https://pubsonline.informs.org/doi/full/10.1287/inte.2026.0314)
- A 2025 arXiv paper on government fiscal documents found LLM accuracy on hierarchical, multi-page tabular data is poorly researched and known to be weak. — [arXiv 2511.10659](https://arxiv.org/abs/2511.10659)
- Milliman published a method for analysing insurance product filings with LLMs (parse and extract data of interest from filings). — [Milliman](https://www.milliman.com/en/insight/analyzing-insurance-product-filings-artificial-intelligence-llm)
- Halcyon uses ML and LLMs to aggregate and organize documents from PUCs, regulators and grid operators. — [Axios Pro](https://www.axios.com/pro/climate-deals/2026/03/16/halcyon-funding-21-million)
- GroundVue (ex-federal technologists) turns hours of recorded public meetings across the US into structured data. — [FedScoop](https://fedscoop.com/former-federal-technologists-tap-public-meetings-data-new-ai-venture/)
- Floodlight and the Texas Tribune produced national/state datasets of data-centre on-site power permits from permit applications as journalism projects (small teams). — [Texas Tribune](https://www.texastribune.org/2026/07/09/texas-data-centers-ai-power-plants-pollution-state-permits/); [Sierra Club report citing Floodlight/EIP](https://www.sierraclub.org/sites/default/files/2026-11/artificialintegrity_report_pdf.pdf)

### Inferences
- At ~$0.002/page, processing 100,000 agenda/permit pages a month costs on the order of a few hundred dollars, which is within a solo budget; this is what makes candidates A, B, D and E newly feasible.
- Narrative documents (agendas, minutes, permit cover sheets, docket filings) are the best fit; dense actuarial exhibits (SERFF) and scanned tables are where accuracy risk concentrates, so Candidate D needs a human-checked sample and field-level validation before selling.
- Because extraction is now cheap for everyone, defensibility shifts to source coverage, freshness (daily alerts), entity resolution across sources, and a narrow buyer workflow; this is also why funded incumbents are expanding quickly and the window for broad products is closing.
- The same cheapness explains the flood of low-priced Apify actors: any single-source feed will be commoditized, so the scarce asset is the cross-source join (e.g. project = zoning case + air permit + large-load docket + queue position).

### Gaps
- No independent accuracy benchmark found for LLM extraction specifically on public-meeting agendas, air-permit applications or SERFF exhibits.
- No data on the ongoing maintenance burden (scraper breakage across hundreds of portals) for a one-person operation.
- The per-page cost is tied to one model's 2026 pricing and one document type; not re-verified against current model prices.
