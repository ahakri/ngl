# Niche data businesses built on web-derived market data: verticals, pricing, and scraping law (as of Nov 2026)

**Method note for the report writer.** Direct page fetches were blocked in this research environment (loeb.com, thenextweb.com and blog.ericgoldman.org all failed DNS resolution), so every finding below rests on web-search result summaries of the cited pages, not on a full read of the page. Where sources conflicted or a figure came from an affiliate/vendor blog, that is flagged inline. Prices marked "third-party" were not confirmed on the vendor's own pricing page.

## 1. What are proven examples and their scale/pricing?

### Takeaway
Web-derived vertical data is a proven model at every scale: self-serve tools at $20-$130/month (Keepa, Jungle Scout, AirDNA, The Odds API, TheirStack), mid-market feeds at $100-$1,000/month (Prisync, HelloData, odds APIs), and enterprise/institutional contracts at $9k-$80k+/year (Cleanview, Sensor Tower, hedge-fund alt data). The largest players are PE/VC-backed (Lightcast/KKR, Lighthouse $370M, Turquoise $95M, Datasembly ~$36M), while the low end contains bootstrapped teams of 1-6 people.

### Cited Findings

**E-commerce pricing (Amazon and general retail)**
- Keepa Pro is reported at EUR 29/month or EUR 290/year after a 2026 increase from EUR 15-19; affiliate-site figure, not confirmed on keepa.com — [RevenueGeeks](https://revenuegeeks.com/keepa-pricing/)
- Keepa API is a separate subscription reported to start at EUR 49/month for 20 tokens/minute, rising to EUR 129 (60), EUR 459 (250) and EUR 879 (500 tokens/min) — [RevenueGeeks](https://revenuegeeks.com/software/keepa/api)
- Jungle Scout tiers run about $29-$129/month billed annually (sources disagree on entry price: $29 annual vs $49 monthly) — [RevenueGeeks](https://revenuegeeks.com/compare/jungle-scout-vs-keepa)
- Prisync (generic competitor price monitoring) lists Premium at $199/month for up to 1,000 products and Platinum at $399/month for up to 5,000, with API access +20% — [Prisync](https://prisync.com/compare-plans)
- A scraping-industry guide claims enterprises pay $5,000-$50,000/month for continuous price monitoring across millions of products (vendor claim, unverified) — [Proxies.sx](https://www.proxies.sx/blog/how-to-sell-web-scraping-api-2026)
- Amazon is now charging the third-party software layer that sellers depend on (relevant platform-dependency risk for Amazon-data tools) — [Marketplace Pulse](https://marketplacepulse.com/articles/amazon-monetizes-the-software-layer-sellers-depend-on)

**Short-term rental**
- AirDNA's Market Research plan is reported at about $34/month billed annually ($400/year) or $125 month-to-month, plus dynamic pricing at $20 per listing per month; older per-market pricing was $19.95-$99.95/month by market size with a global plan at $999.95/month. Third-party sources conflict — [BNBCalc](https://www.bnbcalc.com/blog/airbnb-business/buying-rental-property/airbnb-data-tools-pricing-compared); [AirDNA pricing](https://Airdna.co/pricing)

**Job postings**
- TheirStack's entry tier is listed at $59/month; Coresignal is cited at $49/month by one source and "custom from $250/month" by another; Bright Data sells datasets from $250 per 100,000 records — [Crustdata](https://crustdata.com/blog/best-apis-for-job-posting-data); [TheirStack blog](https://theirstack.com/en/blog/best-job-posting-apis); [Bright Data](https://brightdata.com/blog/web-data/best-job-apis)
- LinkUp and Revelio Labs do not publish prices (use-case/contract-dependent, demo-gated) — [Datarade LinkUp profile](https://www.datarade.ai/data-providers/linkup-job-search-engine/profile); [Bloomberry](https://bloomberry.com/blog/the-best-job-posting-data-providers/)
- TheirStack says it has raised no money and does not plan to; it reports processing 268k jobs/day from 321k sources; one profile lists 3 employees — [TheirStack careers](https://theirstack.com/en/docs/careers); [StartupHub](https://www.startuphub.ai/startups/theirstack)
- Lightcast (formerly Burning Glass/Emsi) has been KKR-owned since 2019 and is still acquiring (Stratigens 2024, others 2025) — [Mergr](https://mergr.com/transaction/kkr-acquires-lightcast); [PE Hub](https://www.pehub.com/kkr-backed-lightcast-bolsters-workforce-data-capabilities-with-stratigens-deal/)

**App-store and ad intelligence**
- Sensor Tower has no public tiers; a vendor blog citing Vendr gives a median annual contract of $75,000 across 40 purchases, with the API add-on at $5,000-$20,000/year; Sensor Tower acquired AppMagic in May 2026 as its SMB offer — [Creatify](https://creatify.ai/de/blog/sensor-tower-pricing-(2026)-plans-credits-and-what-you-ll-actually-pay)
- Appfigures starts at $9.99/user/month — [Capterra](https://capterra.com/p/200383/Sensor-Tower/); [Appfigures pricing](https://appfigures.com/platform/pricing)

**Hotel rates**
- Lighthouse (formerly OTA Insight, hotel rate intelligence) raised a $370M Series C led by KKR — [Hospitality Net](https://www.hospitalitynet.org/news/4124777/lighthouse-announces-370-million-series-c-investment-led-by-kkr-to-accelerate-platform-innovation-and-growth)

**Sports-betting odds**
- The Odds API paid plans start around $30/month for 50,000 credits and run to about $249/month; SportsGameOdds is $99-$499/month; SharpAPI up to $399/month; The Rundown has a free tier — [The Sports Economist](https://thesportseconomist.com/?p=19194); [SportsGameOdds](https://sportsgameodds.com/pricing); [SharpAPI](https://sharpapi.io/pricing); [The Rundown](https://therundown.io/pricing/api)
- OpticOdds has no self-serve tier; a comparison site reports "from around $5,000/month" (secondhand) — [SportsGameOdds comparison](https://sportsgameodds.com/comparing-odds-api-providers/)

**Grocery / retail shelf prices**
- Datasembly collects hyper-local prices from tens of thousands of retail, grocery and QSR locations, mostly from public web sources, sells by subscription, and has raised about $35.5M ($10.3M Series A 2020, ~$7M 2021, $16M Series B 2023) — [BusinessWire](https://www.businesswire.com/news/home/20230519005385/en/Datasembly-Closes-16-Million-Series-B-Funding); [CB Insights](https://www.cbinsights.com/company/datasembly/financials); [TechCrunch](https://techcrunch.com/2020/08/17/datasemblys-real-time-pricing-tool-for-consumer-goods-raises-10-3-million)

**Cannabis retail**
- Headset historically used retailer POS data and has added e-commerce "web-derived" menu data from 7,000+ retailers, for close to 11,000 unique data sources — [Headset](https://headset.io/ecommerce)

**Healthcare price transparency (official machine-readable files rather than scraping)**
- Turquoise Health, founded 2020 on hospital and payer price-transparency disclosures, closed a $40M Series C in March 2026 (total $95.3M) and is pivoting from data provider to contracts/payments workflow — [Fierce Healthcare](https://www.fiercehealthcare.com/health-tech/turquoise-health-raises-40m-power-healthcare-contracts-payments); [MedCity News](https://medcitynews.com/2026/03/turquoise-healthcare-payment/)
- Serif Health (price-transparency data, launched 2020) took its first outside capital only recently, via Seva Growth — [Dealroom](https://dealroom.co/news/146056-serif-health-lands-first-outside-capital-in-seva-growth-deal)

**Heavy equipment**
- EquipmentWatch (with Price Digests) sells tiered subscriptions to contractors, dealers, rental fleets, and a separate finance and insurance plan; no public dollar prices — [EquipmentWatch](https://equipmentwatch.com/plan-finance-insurance/)

**Self-storage**
- StorTrack launched at $49/month per user in 2014 (dated); it was acquired by Green Street in July 2026 and now exposes data through an MCP API — [Inside Self-Storage 2014](https://www.insideselfstorage.com/suppliers-products/stortrack-llc-launches-price-management-service-and-mobile-app-for-self-storage-operators); [Inside Self-Storage 2026](https://www.insideselfstorage.com/suppliers-products/self-storage-data-company-stortrack-expands-ai-support-to-its-model-context-protocol-api)
- TractIQ says it tracks rental rates for 30,000 facilities (70,000+ facilities covered overall); Pro+ includes historic rates and API — [CRE Daily](https://www.credaily.com/reviews/tractiq-review)
- The Self Storage Association data portal is $800/year for members, $1,600 non-members — [SSA](https://selfstorage.org/Products-Services/Research-Data)

**Apartment rents**
- HelloData says it uses only publicly available listing data, tracks comps daily (rent, availability, concessions), and needs no property-management-system integration — [HelloData](https://www.hellodata.ai/apartment-revenue-management-solution)
- HelloData pricing is "contact us" on G2; a Software Advice listing was summarized as $250/user/month plus usage-based API (unverified, third-party) — [G2](https://g2.com/products/hellodata-ai/pricing)

**EV charging**
- Paren sells charging utilization, reliability and pricing data by subscription API/app to charge-point operators, automakers, fleets and mapping services; it raised a $3M seed and acquired EVAdoption; prices not public — [PR Newswire](https://prnewswire.com/news-releases/paren-secures-3m-in-seed-funding-alongside-acquisition-of-evadoption-llc-to-power-unified-electric-mobility-302266327.html); [G2](https://www.g2.com/products/paren-electric-vehicles-charging-insights/pricing)

**Data-centre and power pipeline**
- Cleanview (founded by newsletter writer Michael Thomas) lists its data-centre subscription at $9,000/year and tracks 4,319 campuses and 1,491 data centres under construction — [Cleanview pricing](https://cleanview.co/pricing); [Cleanview tracker](https://cleanview.co/products/data-center-tracker); [Cleanview about](https://cleanview.co/about)

**Small/bootstrapped scraping-adjacent businesses**
- Scrapingdog (scraping API): about $22,000/month revenue, one founder, six employees — [Starter Story](https://www.starterstory.com/stories/how-i-bootstrapped-a-264k-year-data-scrapping-api-from-india)
- A solo developer's scraping API reached >$10K MRR in about 12 months — [Indie Hackers](https://www.indiehackers.com/post/tech/growing-a-scraping-api-to-10k-mrr-in-12-months-6iF8SJRF4WpciDff9aYi)
- Proxycurl (LinkedIn profile data) reached about $10M revenue by the founder's account, then shut down in July 2025 after LinkedIn sued in January 2025 over fake accounts and scraping — [Nubela founder post](https://nubela.co/blog/goodbye-proxycurl/); [Social Media Today](https://www.socialmediatoday.com/news/linkedin-wins-legal-case-data-scrapers-proxycurl/756101/)

### Inferences
- Pricing clusters into three bands, and the band is set by the buyer, not the data: individual operators/sellers pay $20-$130/month; multi-site operators and SMB software teams pay $100-$1,000/month; investors, lenders and enterprises pay $9k-$80k/year.
- The businesses that stayed small and profitable (TheirStack, Keepa-style tools, Cleanview) sell a narrow, well-defined dataset with self-serve or transparent pricing; the ones that raised large rounds are moving up into workflow software (Turquoise, Headset, Lighthouse), which leaves raw-data niches behind them.
- Proxycurl is the cautionary case: its problem was personal data plus fake logged-in accounts on a litigious platform, which is exactly the profile the founder's constraints already exclude.

### Gaps
- No verified revenue figures for AirDNA, Keepa, Jungle Scout, LinkUp, Revelio, Headset, BDSA, StorTrack or Paren were found.
- No current pricing found for DataWeave, BDSA, Hoodie Analytics, Datassential, Technomic, VREF/Aircraft Bluebook, boat valuation services, DAT/Xeneta freight rates, ticket-resale data, or flight-price data.
- TrustMRR/Stripe-verified listings for vertical data businesses were not found; search only surfaced scrapers of TrustMRR itself.
- A bootstrapped "Joblistingdata.com" with about $121K revenue appeared in a search summary but I could not tie it to a specific URL, so it is not cited.

## 2. Which verticals are saturated, and which are underserved or only served at enterprise price points?

### Takeaway
Amazon/e-commerce pricing, job postings, app-store data, sports odds, short-term rentals and generic SaaS-pricing monitors are saturated with cheap self-serve options. Insurance rate filings, data-centre/power pipeline, hospital/payer prices, hotel rates, grocery shelf prices and apartment rents are served mainly by enterprise or funded vendors, leaving room beneath them only where sources are official or bot-tolerant.

### Cited Findings
- Saturated, job postings: at least eight API vendors are compared in 2026 roundups, with entry prices of $49-$59/month — [TheirStack blog](https://theirstack.com/en/blog/best-job-posting-apis); [Bright Data](https://brightdata.com/blog/web-data/best-job-posting-data-providers)
- Saturated, sports odds: multiple APIs with free tiers and $30-$499/month plans — [SportsGameOdds comparison](https://sportsgameodds.com/comparing-odds-api-providers/)
- Saturated, SaaS pricing-page monitoring: more than ten near-identical Apify actors, priced from $4 per 1,000 results, with one claiming 10 pages watched daily costs about $3/month — [Apify example](https://apify.com/renzomacar/saas-pricing-tracker); [Apify example 2](https://apify.com/tagadanar/saas-pricing-monitor)
- Saturated, generic e-commerce price monitoring: Prisync, Price2Spy and many others at $99-$400/month — [Prisync](https://prisync.com/compare-plans); [Shopify roundup](https://www.shopify.com/blog/ecommerce-price-monitoring-tools)
- Enterprise-only, insurance rate filings: incumbents are S&P Global (SNL Insurance Product Filings), Akur8 Discover, ZestyAI and Insuraviews, the last targeting "the top 25 P&C carriers" — [S&P Marketplace](https://www.marketplace.spglobal.com/en/datasets/snl-insurance-product-filings-%281733129635%29); [Akur8](https://akur8.com/pricing/discover); [G2 Insuraviews](https://www.g2.com/products/insuraviews/discuss); [ZestyAI](https://zesty.ai/resource/turn-rate-filings-into-market-intelligence)
- Akur8 reportedly absorbed rate-filing startup Matrisk in January 2026 (single source) — [actuary.info](https://actuary.info/insights/akur8-discover-rate-filing-intel-pc-pricing-actuary-2026)
- Enterprise-priced, data-centre pipeline: Cleanview at $9,000/year; Blackridge sells tiered project databases by seat with sales-quoted prices; TeleGeography sells a Data Center Research Service — [Cleanview](https://cleanview.co/pricing); [Blackridge](https://www.blackridgeresearch.com/new-projects-near-me/data-center-facility-database/c/united-states-us/subscribe); [TeleGeography](https://www2.telegeography.com/hubfs/assets/product-tear-sheets/Data-Center-Research-Service.pdf)
- Consolidating, self-storage: StorTrack bought by Green Street (July 2026); TractIQ and Radius+ also compete — [Inside Self-Storage](https://www.insideselfstorage.com/suppliers-products/self-storage-data-company-stortrack-expands-ai-support-to-its-model-context-protocol-api); [Radius+](https://www.radiusplus.com/?p=2652)
- Thinly served, GLP-1 telehealth pricing: the existing trackers are consumer/affiliate sites or a seller's own index (Weight Loss Rankings covers 273-460 providers; Telehealth Ally 119; Ozari Health, itself a seller, 90+) — [Weight Loss Rankings](https://www.weightlossrankings.org/research/glp1-pricing-index); [Telehealth Ally](https://www.telehealthally.com/guides/glp1-telehealth-pricing-report-q2-2026); [Ozari release](https://www.wboc.com/online_features/press_releases/ozari-health-offers-compounded-semaglutide-from-86-per-month-and-tirzepatide-from-125-per-month/article_de6ed535-bf4f-530a-a04e-8d02a982561a.html)
- Restaurant menu prices are published as free marketing indices by Toast (from its own ~171,000-location POS data) and Datassential (Burger Price Index), signalling incumbents with proprietary first-party data — [Toast](https://pos.toasttab.com/blog/data/menu-price-monitor); [Perishable News](https://perishablenews.com/retailfoodservice/datassential-burger-prices-up-since-2023-while-beef-costs-surge/)

### Inferences
- "Underserved" in practice means "served only by a sales-led enterprise product": insurance filings, data-centre/power pipeline and healthcare prices all have a visible gap between free regulator PDFs and five-figure contracts.
- Verticals where the incumbent has first-party data (Toast POS, Headset POS, RealPage PMS) are poor targets for a scraper: web-derived data is the inferior substitute there.
- Self-storage looks attractive on paper but is three-vendor crowded and just consolidated under a well-capitalised research firm.

### Gaps
- No evidence found either way on used aircraft, boats, freight spot rates, ticket resale, pharmacy cash prices or collectibles; these could not be classified as saturated or underserved from this research.
- The Ozari press-release URL above was taken from a search result list; treat as low-quality promotional sourcing.

## 3. Which verticals have buyers with clear budgets and urgent need, and what do they pay?

### Takeaway
Institutional investors are the best-documented high-budget buyers (about $80k per dataset on average), followed by operators doing competitive pricing, who pay roughly $50-$400/month per seat or site. Insurers, utilities and infrastructure investors pay five figures per year for regulatory and pipeline intelligence.

### Cited Findings
- Money managers spent about $2.8B on alternative data in 2025, up 17%; web-scraped offerings were 15% of spend — [AOL/Business Insider on Neudata](https://www.aol.com/news/money-managers-hungrier-ever-obscure-140001573.html)
- A Neudata survey of 60 buyers found an average of 20 data vendors and $1.6M annual spend, about $80,000 per dataset; large multi-strategy funds average $5M across 43 vendors (survey date unclear) — [Hedgeweek](https://www.hedgeweek.com/hedge-funds-gear-up-for-a-2025-alternative-dataset-budget-boom/)
- Over two-thirds of respondents to Lowenstein Sandler's 2025 survey had alternative-data budgets above $1M — [Lowenstein Sandler](https://www.lowenstein.com/news-insights/firm-news/lowenstein-releases-2025-alternative-data-report-highlighting-rapid-ai-integration-rising-budgets-and-evolving-governance-demands)
- Operators (competitive pricing): Prisync $199-$399/month; AirDNA $34-$125/month; Keepa EUR 29/month; StorTrack historically $49/month per user — [Prisync](https://prisync.com/compare-plans); [BNBCalc](https://www.bnbcalc.com/blog/airbnb-business/buying-rental-property/airbnb-data-tools-pricing-compared); [RevenueGeeks](https://revenuegeeks.com/keepa-pricing/); [Inside Self-Storage](https://www.insideselfstorage.com/suppliers-products/stortrack-llc-launches-price-management-service-and-mobile-app-for-self-storage-operators)
- Infrastructure/energy investors and developers: $9,000/year for a single data-centre tracker — [Cleanview](https://cleanview.co/pricing)
- App publishers and investors: median $75,000/year for Sensor Tower (Vendr data via vendor blog) — [Creatify](https://creatify.ai/de/blog/sensor-tower-pricing-(2026)-plans-credits-and-what-you-ll-actually-pay)
- Insurers: carriers use rate filings for competitive and regulatory intelligence, and S&P publishes a case study of an insurer using filings data for business development — [S&P case study](https://www.spglobal.com/market-intelligence/en/news-insights/case-studies/a-us-insurance-company-uncovers-new-market-insights-drive-business-development); [Milliman](https://us.milliman.com/en/insight/analyzing-insurance-product-filings-artificial-intelligence-llm)
- An idea-analysis site estimates an agency serving med spas would pay $300-$800/month for local market intelligence, and a scraping course lists "daily competitor price feed for [industry]" at $499/month as a productized example (both are estimates, not observed sales) — [IdeasBerg](https://ideasberg.com/ideas/niche-data-refinery-mnnfat); [ScrapingCentral](https://scrapingcentral.com/learn/production-scale/productized-services)

### Inferences
- A solo founder can realistically reach investors only through a marketplace or a few direct relationships; the $80k average reflects vendors with compliance documentation, history and backtests. A realistic solo price to funds is far below the average, and due-diligence questionnaires on collection methods will be asked.
- The most reachable urgent buyers are operators who reprice often and already buy data: multi-site operators, telehealth sellers, insurance product managers/MGAs, and energy/data-centre developers.

### Gaps
- No directly observed price for insurance rate-filing data (S&P, Akur8, Insuraviews all quote privately).
- No lender- or insurer-specific price points for asset-valuation data (equipment, aircraft, boats) were found.

## 4. What is the US/EU legal position on scraping public data for commercial resale, and what keeps a small vendor safe?

### Takeaway
In the US, scraping logged-out public pages remains broadly defensible (CFAA and contract claims have mostly failed against it), but 2025-2026 opened a new front: DMCA section 1201 anti-circumvention claims for bypassing CAPTCHAs and bot detection, where courts have split. In the EU, contract terms and the database right can bind scrapers even for unprotected data, and GDPR applies the moment personal data is involved. The practical safe zone is narrow but clear: no logins or fake accounts, no circumvention of technical blocks, no personal data, facts rather than expressive content, and polite rates.

### Cited Findings

**US: CFAA and contract**
- hiQ v. LinkedIn: the Ninth Circuit's CFAA reasoning favoured the scraper of public pages, but hiQ lost on contract and the case ended with a reported $500K consent judgment and injunction (secondary source) — [DataResearchTools](https://dataresearchtools.com/hiq-linkedin-ruling-scrapers-2026/)
- Meta v. Bright Data (N.D. Cal., Jan 2024): summary judgment for Bright Data on contract claims because Meta's terms bind users and did not reach logged-off scraping of public data; Meta then dropped the case and waived appeal — [Farella Braun + Martel](https://www.fbm.com/intellectual-property/news/scraping-battles-meta-loses-legal-effort-to-halt-harvesting-of-personal-profiles/); [Eric Goldman blog](https://blog.ericgoldman.org/?p=26145)
- X Corp. v. Bright Data (N.D. Cal., May 2024, Judge Alsup): X's contract and state-law claims over scraping were held conflict-preempted by the Copyright Act, since X only holds a non-exclusive licence to user content; access-based claims (trespass to chattels, unfair competition) were also dismissed initially — [Skadden](https://skadden.com/insights/publications/2024/05/district-court-adopts-broad-view); [Davis Polk](https://www.davispolk.com/index%2ephp/insights/client-update/recent-district-court-decision-casts-doubt-terms-use-barring-data-scraping); [Courthouse News](https://www.courthousenews.com/judge-tosses-xs-contract-claims-against-data-scraping-company/)
- A November 26, 2024 order in the same case allowed X to pursue a trespass-to-chattels claim, so server-burden theories remain live — [Harvard TagTeam case summary](https://tagteam.harvard.edu/hub_feeds/3624/feed_items/12701108/content)
- Ryanair v. Booking.com (D. Del.): a July 2024 jury found a CFAA violation with exactly $5,000 in loss; in January 2025 Judge Bryson granted judgment as a matter of law for Booking, finding only $2,457.72 of loss attributable, below the CFAA's $5,000 threshold — [Eric Goldman blog](https://blog.ericgoldman.org/archives/2025/03/court-overturns-a-bad-jury-verdict-against-scraping-ryanair-v-booking-guest-blog-post.htm); [Cooley](https://www.cooley.com/news/coverage/2025/2025-01-22-cooley-secures-decisive-win-for-bookingcom-in-computer-fraud-and-abuse-act-case); [Bloomberg Law](https://news.bloomberglaw.com/litigation/booking-com-wins-reversal-of-verdict-for-ryanair-scraping-case)
- LinkedIn sued Proxycurl in January 2025 over fake accounts and scraping; Proxycurl shut down July 2025 rather than litigate, the founder citing the American Rule on fees and Microsoft's resources; LinkedIn sued another scraper (ProAPIs) in October 2025 — [Nubela](https://nubela.co/blog/goodbye-proxycurl/); [LinkedIn](https://news.linkedin.com/2025/LinkedInWinsLegalBattleToProtectMemberData); [Bloomberg Law](https://news.bloomberglaw.com/artificial-intelligence/linkedins-war-against-bot-scrapers-ramps-up-as-ai-gets-smarter)

**US: the DMCA section 1201 front (2025-2026)**
- Ziff Davis v. OpenAI (S.D.N.Y., Dec 2025, Judge Stein): robots.txt is not a "technological measure that effectively controls access"; it is like a "keep off the grass" sign, and ignoring it is not circumvention. The ruling is narrow and does not say scraping is lawful — [Eric Goldman blog](https://blog.ericgoldman.org/archives/2025/12/are-robots-txt-instructions-legally-binding-ziff-davis-v-openai.htm); [ChatGPT Is Eating the World](https://chatgptiseatingtheworld.com/2025/12/16/judge-stein-rejects-ziff-davis-dmca-claim-based-on-openais-alleged-circumvention-of-robots-txt-judge-shuts-down-novel-theory-b-c-robots-txt-does-not-control-access/)
- Google v. SerpApi (N.D. Cal., 20 July 2026, Chief Judge Gonzalez Rogers): Google's DMCA claims dismissed, reasoning that section 1201 protects only measures guarding copyrighted works; dismissal reported as without prejudice — [The Next Web](https://thenextweb.com/news/google-serpapi-dmca-scraping-lawsuit-dismissed); [Techdirt](https://www.techdirt.com/tag/dmca/)
- Reddit v. SerpApi/Perplexity (S.D.N.Y., 31 July 2026, Judge Engelmayer): Reddit's section 1201(a) anti-circumvention claims mostly survived dismissal; CAPTCHA and bot-detection systems can qualify as access controls even though humans can view the content; the 1201(b) claim was dismissed — [Loeb & Loeb](https://www.loeb.com/en/insights/publications/2026/08/reddit-v-serpapi-llc); [MLex](https://www.mlex.com/mlex/articles/2508237/us-judge-allows-reddit-anti-circumvention-claims-vs-perplexity-ai-serpapi); [Law360](https://www.law360.com/ip/articles/2508228)
- Commentators note plaintiffs moved to section 1201 precisely because it avoids the copyright-preemption problem from X Corp. v. Bright Data — [ZwillGen](https://www.zwillgen.com/alternative-data/how-artificial-intelligence-shaping-web-scraping-litigation/); [Bloomberg Law](https://news.bloomberglaw.com/ip-law/reddit-has-given-content-hosts-an-upper-hand-against-ai-scraping)
- Contrary views: analysts argue DMCA claims against scrapers face long odds and that anticircumvention law is the wrong tool — [Capstone](https://capstonedc.com/?p=54364); [Authors Alliance](https://www.authorsalliance.org/2026/01/08/anticircumvention-law-is-not-the-right-solution-to-webscraping/)

**Robots.txt and AI-crawler disputes**
- Cloudflare began blocking AI crawlers by default for new customers on 1 July 2025 and launched Pay Per Crawl in private beta — [MIT Technology Review](https://www.technologyreview.com/2025/07/01/1119498/cloudflare-will-now-by-default-block-ai-bots-from-crawling-its-clients-websites/amp/); [The Register](https://www.theregister.com/2025/07/01/cloudflare_creates_ai_crawler_toll/)
- A July 2026 report says Pay Per Crawl is being rebranded "Pay Per Use" and that from 15 September Cloudflare would block AI-training crawlers on any page carrying ads unless the owner opts in (single source) — [The Next Web](https://thenextweb.com/news/cloudflare-block-ai-crawlers-pay-publishers?type=AI)

**EU**
- Ryanair v PR Aviation (CJEU C-30/14, 2015): where a database is protected by neither copyright nor the sui generis right, the Database Directive's user exceptions do not apply, so the site owner is free to restrict scraping by contract terms — [Pinsent Masons](https://www.pinsentmasons.com/out-law/news/website-operators-can-prohibit-screen-scraping-of-unprotected-data-via-terms-and-conditions-says-eu-court-in-ryanair-case)
- Commercial text and data mining is permitted under Article 4 of the CDSM Directive subject to a machine-readable rightsholder opt-out; how a valid opt-out is expressed remains unsettled, and in October 2025 a Danish court held a scraping prohibition in a public HTML policy could qualify as a reservation — [Kluwer Copyright Blog](https://legalblogs.wolterskluwer.com/copyright-blog/laion-round-2-machine-readable-but-still-not-actionable-the-lack-of-progress-on-tdm-opt-outs-part-1/); [Reed Smith](https://www.reedsmith.com/articles/entertainment-media-guide-to-ai-three-years-on/text-data-mining-in-the-eu/)
- The EDPB published web-scraping guidelines (July 2026): GDPR applies whenever scraping includes personal data; legitimate interest is the usual basis with a three-part test; robots.txt, CAPTCHAs and login walls are reportedly relevant to the balancing test — [EDPB](https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_2020603_webscraping_v1_en_0.pdf); [Reed Smith](https://www.reedsmith.com/our-insights/blogs/technology-law-dispatch/102nbqu/edpb-web-scraping-guidelines-for-ai-making-the-impossible-possible/)
- The CNIL's scraping focus sheet states scraping may be prohibited by other rules such as terms of use based on database-producer rights or copyright — [CNIL](https://www.cnil.fr/en/legal-basis-legitimate-interests-focus-sheet-measures-implement-case-data-collection-web-scraping)
- The Dutch regulator's scraping guidance warns businesses of GDPR breach risk — [Pinsent Masons](https://www.pinsentmasons.com/de-de/out-law/nachrichten/dutch-web-scraping-guidance-warn-businesses-gdpr-breach-risk)

### Inferences
Practices that keep a small vendor on defensible ground, derived from the cases above:
- **Stay logged out; never create accounts.** Meta v. Bright Data turned on logged-off access; Proxycurl was sued over fake accounts. Clicking "I agree" or logging in creates the contract that the Bright Data cases found missing.
- **Do not defeat CAPTCHAs, bot detection or IP blocks.** After Reddit v. SerpApi this is the single largest new US risk; robots.txt alone is not an access control (Ziff Davis), but active circumvention may be. If a source blocks you, drop it or license it. This aligns with the founder's restricted-network constraint: avoid any niche that needs anti-bot evasion.
- **Collect facts, not expression.** Prices, rates, availability, counts and filing metadata are not copyrightable; photos, descriptions and reviews are. Store and resell the numbers, not the page.
- **No personal data.** Business/market data keeps the product outside GDPR, the EDPB guidelines and US state privacy law.
- **Keep load trivial.** Trespass-to-chattels survived in X v. Bright Data and CFAA "loss" was the pivot in Ryanair v. Booking; low request rates and off-peak crawling keep both theories weak.
- **Prefer official feeds and public-record sources** (regulator filings, mandated machine-readable files, public APIs): no ToS problem, no anti-bot problem, and no database-right problem.
- **For EU sources, treat ToS and database right as real constraints.** Ryanair v PR Aviation means EU site terms can bind; a US-focused product built on US sources avoids most of this.
- **Deliver aggregated/derived outputs** (indices, change logs, normalised tables) rather than mirroring a source's catalogue, which reduces both database-right and "free-riding" arguments.
- **Litigation cost, not doctrine, is the real threat to a solo founder.** Proxycurl folded without a ruling. Avoid sources owned by known litigants (LinkedIn/Microsoft, Meta, X, Reddit, Ryanair, Google; CoStar is my addition from general knowledge, not from these searches).

### Gaps
- I could not confirm whether X Corp. v. Bright Data was appealed or settled, or whether Ryanair appealed the January 2025 ruling, or whether Google refiled against SerpApi.
- No 2025-2026 CJEU ruling on the sui generis database right and scraping was found (CV-Online Latvia v Melons was searched for but not retrieved).
- The Hamburg LAION ruling's reasoning and appeal status were not retrieved.
- I found no US case in 2025-2026 specifically about a small vendor reselling scraped price/listing facts; the precedent is almost entirely large platforms versus large scrapers or AI companies.
- Law-firm client alerts could only be seen through search summaries because fetches were blocked.

## 5. The most promising underserved verticals for a solo founder

### Takeaway
The best fits combine official or bot-tolerant sources with buyers who already pay five figures to enterprise vendors: state insurance rate filings, data-centre/power infrastructure pipeline, and GLP-1/telehealth cash pricing lead; healthcare price-transparency slices, EV charging prices and tariff-driven price indices are plausible; apartment rents and self-storage have demand but worse source and competition profiles.

### Cited Findings

**A. State insurance rate filings (home and auto)**
- Sources: regulators publish SERFF-derived rate-change data openly. Oklahoma posts monthly homeowners and auto reports with company, tracking number, effective dates and overall rate impact; Tennessee publishes monthly homeowners rate changes with overall/max/min impact and policies affected; Texas offers an exportable rate-filing dataset; Maine posts weekly P&C rate-change lists; Arkansas has a public portal — [Oklahoma](https://www.oid.ok.gov/wp-content/uploads/2026/09/HO-Jan-2026-Aug-2026-SERFF-State-Rate_change-Report.pdf); [Tennessee](https://www.tn.gov/commerce/insurance/consumer-resources/homeowners-automotive-insurance-information/homeowners-rates.html); [Texas](https://tdi.texas.gov/consumer/home-and-auto-insurance-rate-filings.html); [Maine](https://www.maine.gov/pfr/insurance/sites/maine.gov.pfr.insurance/files/inline-files/PC%20rate%20changes%20as%20of%2010-09-2026.pdf); [Arkansas](https://portal.insurance.arkansas.gov/complianceratechangespublic/compliance-rate-changes/index)
- The Chicago Fed builds a homeowners rate index from SERFF via S&P Capital IQ Pro, weighting approved changes by premium affected (a methodology template) — [Chicago Fed](https://www.chicagofed.org/research/content-areas/insurance-initiative/pc-data)
- NAIC notes researchers usually access filings through commercial vendors rather than the regulatory systems directly; SERFF is mid-way through a multi-year modernisation — [NAIC CIPR](https://content.naic.org/sites/default/files/cipr-report-appendix-advice-to-researchers.pdf); [NAIC SERFF](https://content.naic.org/index.php/industry/serff)
- Competitors: S&P Global, Akur8 Discover (acquired Matrisk), ZestyAI, Insuraviews, RateFilings.com, all enterprise/sales-led — [S&P](https://www.marketplace.spglobal.com/en/datasets/snl-insurance-product-filings-%281733129635%29); [Akur8](https://akur8.com/pricing/discover); [CB Insights](https://www.cbinsights.com/compare/national-underwriter-vs-ratefilingscom)

**B. Data-centre and power-infrastructure pipeline**
- Cleanview shows a newsletter-founder-led company can sell a building-level tracker at $9,000/year, including utility and power-market attribution — [Cleanview pricing](https://cleanview.co/pricing); [Cleanview tracker](https://cleanview.co/products/data-center-tracker)
- interconnection.fyi exists as a small co-founded business selling "real-time national interconnection data" (pricing not found) — [Substack profile](https://ctalley.substack.com/about)
- Competitors at higher price: Blackridge project databases, TeleGeography research service — [Blackridge](https://www.blackridgeresearch.com/new-projects-near-me/data-center-facility-database/c/united-states-us/subscribe); [TeleGeography](https://www2.telegeography.com/hubfs/assets/product-tear-sheets/Data-Center-Research-Service.pdf)

**C. GLP-1 / telehealth cash-price tracking**
- Roughly 90-460 telehealth providers publish prices; one tracker reports a July 2026 median of $175/month and a floor of $49; another shows the range narrowing from $99-$299 (Q4 2025) to $129-$199 (Q2 2026) — [Weight Loss Rankings](https://www.weightlossrankings.org/research/glp1-pricing-index); [Weight Loss Rankings floor](https://www.weightlossrankings.org/research/cheapest-compounded-semaglutide); [Telehealth Ally](https://www.telehealthally.com/guides/glp1-telehealth-pricing-report-q2-2026)
- The compounded market is shrinking under FDA enforcement; one roundup counts eight major providers still offering compounded semaglutide as of April 2026 — [Telehealth Ally](https://www.telehealthally.com/compare/compounded-semaglutide-providers-roundup)

**D. Healthcare price-transparency slices**
- Source data are federally mandated machine-readable files; the leader (Turquoise, $95.3M raised) is moving to workflow/payments; only about half of hospital files analysed were fully compliant (2024) — [Fierce Healthcare](https://www.fiercehealthcare.com/health-tech/turquoise-health-raises-40m-power-healthcare-contracts-payments); [HealthExec](https://healthexec.com/topics/healthcare-management/business-intelligence/healthcare-price-transparency-startup-earns-40m-seed-funding-bringing-total-95m)

**E. EV fast-charging prices**
- Paren reports average fast-charging prices around $0.53/kWh in Q1 2026 and that the US network passed 80,000 fast-charging ports in Q3 2026; buyers include charge-point operators, automakers, fleets, mapping services, and the Transportation Energy Institute partnered with Paren in January 2026 — [Electrek](https://electrek.co/2026/04/23/ev-fast-charging-is-stabilizing-in-the-us-heres-what-changed/?extended-comments=1); [EV Infrastructure News](https://www.evinfrastructurenews.com/charging-installation/us-fast-charging-network-q3-2026-tesla-market-share); [NACS](https://www.convenience.org/Media/Daily/2026/January/13/5-TEI-Partners-With-Paren_Tech)

**F. Apartment rents from public listings**
- The DOJ's proposed RealPage settlement (Nov 2025) bars use of competitors' nonpublic data in real-time pricing and limits training to nonpublic data at least 12 months old; California and New York passed laws on rent-setting software and cities such as Philadelphia and Seattle passed ordinances — [DOJ](https://www.justice.gov/opa/pr/justice-department-requires-realpage-end-sharing-competitively-sensitive-information-and); [NPR](https://www.npr.org/2025/11/25/g-s1-99331/realpage-rent-algorithm-limits-settlement); [Paul Weiss via CLS Blue Sky](https://clsbluesky.law.columbia.edu/2025/12/04/paul-weiss-discusses-dojs-algorithmic-pricing-settlement/)
- HelloData positions on "only publicly available data" — [HelloData](https://www.hellodata.ai/apartment-revenue-management-solution)

**G. Self-storage street rates**
- TractIQ notes most operators will not share rate data with potential competitors, so web-collected street rates are the standard source — [CRE Daily](https://www.credaily.com/reviews/tractiq-review)

### Inferences
Assessment table (my judgment, built from the findings above; buyer prices are estimates anchored on the cited comparables, not observed quotes):

| Vertical | Who buys | Plausible price | Sources to cover | Collection difficulty | Legal risk | Solo fit |
|---|---|---|---|---|---|---|
| A. Insurance rate filings | Carrier product/pricing teams, MGAs, agencies, reinsurance and equity analysts, journalists | $200-$1,000/mo self-serve; $5k-$20k/yr team (anchored below S&P/Akur8 enterprise deals) | ~10-51 state portals; start with the 5-10 that publish structured reports | Low for state reports (PDF/CSV); SERFF Filing Access itself is harder (per-state terms, session-based UI) | Low: public regulatory records, no personal data | High |
| B. Data-centre / power pipeline | Developers, utilities, equipment suppliers, infrastructure investors, lenders | $3k-$9k/yr (Cleanview anchor $9k) | ISO/RTO queues (7 ISOs plus utilities), state PUC dockets, county permits | Low to medium: official downloads, but heterogeneous and labour-heavy to normalise | Low | Medium-high; Cleanview and interconnection.fyi already occupy it, so a sub-niche (e.g. large-load tariffs, substation/transformer filings) is needed |
| C. GLP-1 / telehealth pricing | Telehealth operators (repricing), pharma market-access teams, investors, pharmacies | $300-$1,500/mo to operators/analysts | ~100-450 provider pricing pages | Low: static marketing pages meant to be read | Low-medium: public prices; avoid medical-claim content and affiliate conflicts | High now, but market durability is uncertain as compounding shrinks |
| D. Price-transparency slices | Provider-group contracting teams, self-insured employers, benefit consultants | $5k-$25k/yr per specialty/region slice | Mandated files from hospitals/payers | No anti-bot, but files are enormous (compute/storage heavy) | Low: mandated public disclosure | Medium; pick one specialty or region |
| E. EV charging prices | Charge-point operators, c-stores, utilities, fleet managers | $200-$1,000/mo | A handful of network apps/APIs plus federal station registries | Medium: prices often live in apps, not pages | Medium: app/API terms | Medium; Paren is funded and entrenched |
| F. Apartment rents | Owners/operators, lenders, appraisers | $100-$250/user/mo (HelloData anchor, unverified) | Thousands of property sites or a few listing portals | High: portals use heavy anti-bot; property sites are fragmented | Medium-high: listing portals are litigious and now DMCA 1201 exposure if blocks are bypassed | Low |
| G. Self-storage rates | Operators, developers, lenders | $50-$300/mo | Large-operator sites plus aggregators | Medium | Low-medium | Low: three incumbents, one just acquired by Green Street |

- Number-of-sources and difficulty ratings are my assessments; the research did not test any source for anti-bot behaviour.
- A and B share a structural advantage for the founder's restricted-network build environment: the sources are a modest number of stable government or quasi-official endpoints that tolerate automated retrieval.

### Gaps
- No direct evidence of willingness-to-pay from mid-market insurance buyers (MGAs, agencies) for a cheaper rate-filing product; the incumbents' focus on top-25 carriers is the only signal.
- SERFF Filing Access terms of use per state were not reviewed; some states may restrict bulk or commercial reuse.
- interconnection.fyi pricing and revenue were not found.
- Utility-tariff/electricity-rate data vendors (e.g. Arcadia/Genability) and freight, aircraft, boat and ticket data were not researched in enough depth to rank.

## 6. Verticals where data became newly valuable in 2025-2026

### Takeaway
Tariffs, the data-centre/power buildout, insurance repricing, GLP-1 price wars, rent-algorithm regulation and AI-agent commerce each created fresh demand for clean, timely price or pipeline data in 2025-2026. The first three map onto official or bot-tolerant sources; agent commerce is being captured by platform feeds rather than scrapers.

### Cited Findings
- Tariffs: Cavallo's team built a tariff tracker on daily PriceStats-scraped prices from five large US retailers (350,000+ goods), estimating about 20% retail pass-through and roughly 0.7 points added to CPI by September 2025; a March 2026 Fed note finds at least 30% pass-through for Chinese goods between April and December 2025; central banks (Minneapolis Fed, Bank of Canada) cite the data — [NBER w34496](https://www.nber.org/papers/w34496); [Pricing Lab tracker](https://pricinglab.org/tariff-tracker); [Minneapolis Fed](https://www.minneapolisfed.org/article/2025/daily-pricing-data-reveal-the-slow-rolling-impact-of-tariffs); [Federal Reserve FEDS Note](https://federalreserve.gov/econres/notes/feds-notes/the-slow-climb-how-tariffs-gradually-raised-retail-prices-in-2025-20260305.html)
- Insurance: state regulators now publish monthly SERFF rate-change reports showing individual filings such as +13.0% (USAA General Indemnity) and +7.7% (Hartford) in Oklahoma homeowners in 2026 — [Oklahoma Insurance Department](https://www.oid.ok.gov/wp-content/uploads/2026/09/HO-Jan-2026-Aug-2026-SERFF-State-Rate_change-Report.pdf)
- Insurance: actuarial consultancies are applying LLMs to filings, lowering the cost of structuring them — [Milliman](https://us.milliman.com/en/insight/analyzing-insurance-product-filings-artificial-intelligence-llm)
- Data centres: a single tracker lists 1,491 data centres under construction and sells at $9,000/year — [Cleanview](https://cleanview.co/products/data-center-tracker)
- GLP-1: telehealth compounded-semaglutide prices fell and compressed between Q4 2025 and Q2 2026, and at least three independent price indices launched — [Telehealth Ally](https://www.telehealthally.com/guides/glp1-telehealth-pricing-report-q2-2026); [Weight Loss Rankings 12-month movement](https://www.weightlossrankings.org/research/compounded-glp1-price-movement-12-months)
- Housing: the RealPage settlement and state/city laws push rent-pricing tools toward public data only — [DOJ](https://www.justice.gov/opa/pr/justice-department-requires-realpage-end-sharing-competitively-sensitive-information-and); [ProPublica](https://www.propublica.org/article/doj-realpage-settlement-rental-price-fixing-case)
- AI-agent commerce: OpenAI's Product Feed Specification takes merchant feeds (CSV/TSV/XML/JSON) updated as often as every 15 minutes; Feedonomics launched Agentic Catalog Exports to seven AI surfaces in April 2026; Shopify reports AI-referred orders up nearly 13x year over year in Q1 2026 (vendor figure); Gartner predicts 20% of transactions via AI platforms/agents by 2030 — [Forrester](https://www.forrester.com/blogs/a-holiday-season-gift-wrapped-in-agentic-commerce); [dev.to on Feedonomics](https://dev.to/searchless_ai/feedonomics-launches-agentic-catalog-exports-how-products-enter-the-ai-shopping-pipeline-51b0); [Shopify](https://www.shopify.com/enterprise/blog/agentic-commerce-executive-guide); [Gartner](https://www.gartner.com/en/documents/7342030)
- EV charging: public fast-charging kept expanding despite the EV sales slowdown — [Axios](https://axios.com/2026/02/04/tesla-supercharger-ev-public-charging)
- Restaurant inflation: burger menu prices are up about 14% since January 2023 per Datassential's index — [Perishable News](https://perishablenews.com/retailfoodservice/datassential-burger-prices-up-since-2023-while-beef-costs-surge/)
- Self-storage: street rates fell 2.2% year over year by August 2026, keeping operators focused on competitor pricing — [RentCafe](https://www.rentcafe.com/blog/?p=151237)

### Inferences
- Tariff price tracking is valuable but the proven version scrapes the five largest US retailers, which are the most heavily bot-defended sites on the web; a solo-feasible variant would pair the official tariff schedule with a small set of tolerant category sources (e.g. manufacturer price lists), which this research did not validate.
- Agent commerce increases the value of clean product data, but merchants push it through first-party feeds (OpenAI spec, Shopify Catalog, Feedonomics), so there is little room for a third-party scraper to sell the same data.
- The post-RealPage shift is a real tailwind for public-data rent comps, but HelloData already holds that position and the sources are hostile.

### Gaps
- No sources found on energy-price datasets (retail electricity tariffs, large-load tariffs) as a 2025-2026 opportunity, despite being named in the brief.
- No evidence on TrumpRx or pharmacy cash-price datasets was found.
- No evidence of what tariff-exposed mid-market buyers (importers, distributors) pay for price-tracking data.
