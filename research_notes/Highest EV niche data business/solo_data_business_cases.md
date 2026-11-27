# Solo-founder / bootstrapped data businesses with known revenue: evidence base and patterns

Research date: 2026-11-27. Method note: findings come from web search result summaries; direct page fetches of Indie Hackers, Starter Story, Apify blog, nubela.co, wearefounders.uk and beehiiv were blocked by this session's network allowlist, so figures below are as surfaced by search snippets and were NOT re-read on the primary page. Verification labels used throughout:
- **[F]** founder-stated (own post/podcast/blog)
- **[3P]** third-party write-up of a founder claim (Starter Story, newsletters, podcasts notes)
- **[EST]** third-party model estimate (Latka, ZoomInfo, Sacra, StartupHub) — treat as weak
- **[NONE]** no revenue figure found

No case below is Stripe-verified by me; I could not open TrustMRR category pages.

## Which solo/small-team data businesses have publicly verified or credibly reported revenue? (case table: niche, source, buyer, pricing, revenue, team, time to first revenue, channel)

### Takeaway
I found about 25 cases, but only around 10 have a founder-stated, dated revenue figure; the rest are third-party estimates or have no figure at all. The credible solo/bootstrapped wins cluster in (a) B2B lead-generation databases (BuiltWith, Store Leads, Who Sponsors Stuff, Proxycurl), (b) developer-facing scraped-data APIs (SerpApi, Scrape Creators, EODHD, IPinfo), and (c) a few paid research newsletters (Trends.vc); small "funded-startup lead list" products exist but sit at $1.5-2.5K/month.

### Cited Findings

**A. Lead-generation / B2B prospecting databases**

1. **BuiltWith** (website technology profiles; crawled from public sites; buyers = sales/marketing teams prospecting by tech stack).
   - Widely repeated figure of about $14M/year with "zero employees"; this comes from secondary write-ups, not audited or founder-published financials [3P]. — [Indie Hackers post](https://www.indiehackers.com/post/how-builtwith-generates-14-million-a-year-while-having-zero-employees-fb97f1e42c); [5to9 newsletter, 2023](https://5to9.beehiiv.com/p/builtwith-generates-14-million-year-zero-employees)
   - Starter Story's profile shows internally inconsistent figures ($215K/month in one place and $1.17M/month in another), so its numbers should be discounted. — [Starter Story](https://www.starterstory.com/stories/builtwith-technology-lookup-breakdown)
   - Began as Gary Brewer's solo side project while employed; Andrew Rogers later joined as co-founder, so "solo" is accurate only for early years. — [Andrew Rogers, Medium](https://medium.com/@andrewjrogers/the-story-of-builtwith-e3bbc17c239f)
   - Early growth lever reported as a distribution partnership: AboutUs added BuiltWith links to its directory records, reportedly 10x-ing traffic [3P]. — [Indie Hackers post](https://www.indiehackers.com/post/how-builtwith-generates-14-million-a-year-while-having-zero-employees-fb97f1e42c)

2. **Store Leads** (database of e-commerce stores; crawled; buyers = Shopify app vendors, agencies, outbound sales teams).
   - Revenue: only a model estimate of about $982K/year (range $597K-$2.1M, "72% confidence", based on comparables, not disclosures) [EST]. — [StartupHub](https://www.startuphub.ai/startups/storeleads)
   - Scale described as 13.7M+ stores across 405 platforms, ~60 filters, weekly refresh; it does not supply verified decision-maker emails, so buyers pair it with enrichment. — [TrendTrack review](https://www.trendtrack.io/blog-post/store-leads-review)
   - Pricing listed at $75/month (1 user) and $250/month (3 users); may be outdated. — [G2](https://www.g2.com/products/store-leads)
   - Origin: founder built it as a by-product of promoting his own Shopify app (2018 post). — [Indie Hackers](https://www.indiehackers.com/product/store-leads/shopify-app-market-research--LQ-lzDy5giDiked5JpR)

3. **Wappalyzer** (tech-stack detection; browser extension + crawler; buyers = sales/lead-gen, security).
   - Founded 2008 by Elbert Alias. — [Wappalyzer About](https://wappalyzer.com/about)
   - Latka lists an estimated $18M 2024 revenue with a team of 3 [EST — unconfirmed, I would not rely on it]. — [Latka](https://getlatka.com/companies/wappalyzer)
   - I found no evidence of an acquisition in search results.

4. **Proxycurl** (LinkedIn-derived people/company enrichment API; scraped; buyers = sales-tech and recruiting-tech developers).
   - Founder Steven Goh described the company as on track for $10M ARR, bootstrapped; founder also wrote about cold-emailing to $1M ARR in 18 months [F]. — [Indie Hackers: cold-emailed to $1M ARR](https://www.indiehackers.com/post/i-cold-emailed-our-way-to-1m-arr-in-18-months-heres-the-story-dc078b4321); [founder shutdown post](https://nubela.co/blog/goodbye-proxycurl/)
   - About 50% of revenue came from scraping LinkedIn [F]. — [founder shutdown post](https://nubela.co/blog/goodbye-proxycurl/)
   - LinkedIn sued in January 2025; service ended 4 July 2025. See failures section. — [Social Media Today](https://www.socialmediatoday.com/news/linkedin-wins-legal-case-data-scrapers-proxycurl/756101/)

5. **NinjaPear** (B2B enrichment data; successor project associated with the Proxycurl founder's blog domain).
   - Indie Hackers post titled "Hitting $15k/mo six months after getting sued and acquired"; search summary reports over $15K gross revenue "last month" [F, undated in my results; I could not open the page to confirm date or that it is the same founder]. — [Indie Hackers](https://www.indiehackers.com/post/MMWkpCaClOB6wVgbuPI7)

6. **Who Sponsors Stuff** (database of which brands sponsor which email newsletters; manually/semi-manually tracked from 400-500+ newsletters; buyers = newsletter ad sales teams).
   - Two co-founders (Ryan Sager, Jesse Watkins), ex-Ladders newsletter ad sales; product grew out of their own prospecting database. — [SparkLoop podcast](https://sparkloop.app/blog/s01e17-how-to-sell-more-newsletter-ads-sponsorships-in-2023-and-beyond-with-ryan-sager-jesse-watkins-from-who-sponsors-stuff)
   - Reported at about $100K/year, described as a no-code database sold as annual licences; a secondary roundup says six-figure revenue within a year of starting in late 2021 [3P]. — [Indie Hustle](https://indiehustle.beehiiv.com/p/this-no-code-database-about-sponsors-brings-in-100-000-a-year); [Koerner Office ep. 060](https://metacast.app/podcast/the-koerner-office---business-ideas-and-small/lwDrEPcr/060-a-100k-year-no-code-sponsor-database/fYxTYwjk)

7. **VCbacked** (searchable database of VC-funded startups + contacts; mixed sources incl. scraping; buyers = marketing agencies).
   - About $1.5K/month ($18K/year) as a solo side project, October 2023; founder spends ~70% of time updating the database and ~30% on outreach [F via Starter Story]. — [Starter Story](https://www.starterstory.com/stories/vcbacked)

8. **Fuelblock Leads** (monthly list of newly funded early-stage startups; subscription).
   - $2.5K/month as a side hustle, May 2023; first customer was a VC firm [F via Starter Story]. — [Starter Story](https://www.starterstory.com/stories/fuelblock)

9. **Growth List / Fundraise Insider** (funded-startup lead lists; free list of 100 as lead magnet, premium ~57,000 companies; weekly list of 250+ funded-company contacts). Both rely on programmatic SEO "List of funded X startups (2026)" pages. Revenue [NONE]. — [Growth List](https://growthlist.co/funded-startups/); [Fundraise Insider](https://fundraiseinsider.com/blog/b2b-saas-companies/)

**B. Developer-facing data APIs**

10. **SerpApi** (Google/other search results as JSON; scraped; buyers = SEO tools and, increasingly, AI companies).
    - Bootstrapped since 2017, profitable, ~35 employees. — [Sacra](https://sacra.com/c/serpapi/)
    - Revenue estimates conflict: ~$3M ARR vs $8.4M [EST, neither company-reported]. — [everydev.ai](https://www.everydev.ai/developers/serpapi); [ZoomInfo](https://www.zoominfo.com/c/serpapi/457147457)
    - About 40% of business comes from AI startups (founder statement reported by The Information; excludes NDA customers). — [The Information](https://feature.theinformation.com/newsletters/ai-agenda/meet-google-scraping-startup-used-chatgpt-cursor-perplexity)

11. **Scrape Creators** (real-time social media data API — TikTok/Instagram/YouTube etc.; scraped; usage/credit pricing; buyers = developers of creator/marketing tools).
    - Solo founder Adrian Horning; launched June 2024; "$10k+ MRR in 12 months"; was paying most of his bills by March 2025 [F]. — [Indie Hackers](https://www.indiehackers.com/post/6iF8SJRF4WpciDff9aYi); [We Are Founders](https://www.wearefounders.uk/from-side-projects-to-10k-mrr-how-adrian-horning-built-scrape-creators/)
    - Later reported at about $20K/month, with roughly 12 heavy users producing most revenue [3P summary of a Starter Story interview]. — [BetterLaunch playbook](https://www.betterlaunch.co/playbooks/episodes/adrian-scrape-creators)
    - Growth attributed mainly to organic social and personalised outreach on X, plus some paid ads. — [Starter Story growth channels](https://www.starterstory.com/businesses/scrape-creators/growth-channels)

12. **EODHD (EOD Historical Data)** (financial market data API; buyers = retail quants, fintech developers).
    - Founder Denis Alaev: $0 to $3.5M ARR; started 2015 as a robo-advisory engine and pivoted to API-first data delivery [F, paywalled]. — [Indie Hackers](https://www.indiehackers.com/post/Lr06SBW8hccsjlJBV10K)
    - Bootstrapped "from a $10 server" to 17 servers. — [daily.dev](https://app.daily.dev/posts/how-we-bootstrapped-eodhd-apis-from-a-10-server-to-a-global-data-infrastructure-6oc68cqov)
    - HackerNoon piece by the founder dated April 2025. — [HackerNoon](https://hackernoon.com/how-eodhd-apis-quietly-built-a-six-figure-business-by-fixing-financial-data)

13. **IPinfo** (IP geolocation/ASN data API and downloads; own measurement infrastructure; buyers = developers, security, enterprises).
    - Started as Ben Dowling's side project while at Facebook/Calm; was earning more than his Calm CTO salary before he went full-time; later described as a 7-figure, "multiple millions" bootstrapped SaaS [F via podcast; the "multiple millions" phrasing may be the host's]. — [SaaS Club](https://saasclub.io/podcast/ipinfo-ben-dowling/); [Bootstrappers](https://bootstrappers.com/how-the-former-cto-of-calm-made-millions-after-realizing-enterprises-will-pay-generously-for-good-data/)
    - Team grew from ~15 to 36 employees; still "bootstrapped & steady". — [IPinfo About](https://ipinfo.io/about)

14. **Listen Notes** (podcast search engine + Listen API + datasets + alerts; RSS-derived; one-person company).
    - Started as a side project December 2016; API became "a core part of the business" and grew enough that RapidAPI's 20% cut was too much, so it moved off the marketplace [F]. Revenue [NONE]. — [Listen Notes blog](https://www.listennotes.com/blog/how-i-accidentally-built-an-api-business-46/)

15. **Podscan** (podcast transcript monitoring + API/firehose; Arvid Kahl; plans from ~$100/month).
    - About $1K MRR two months after launch (May 2024) [F]. — [Bootstrapped Founder ep. 317](https://goodpods.com/podcasts/the-bootstrapped-founder-190792/317-podscan-2-months-and-1k-mrr-in-50662029)
    - Took "a six-figure amount" of funding in April 2024. — [Podnews](https://podnews.net/directory/company/podscan)
    - April 2025: ~$6K MRR against ~$10K monthly expenses (down from ~$30K); briefly profitable for two months until one major customer churned [F]. — [The Bootstrapped Founder](https://thebootstrappedfounder.com/when-profitability-disappears-a-podscan-reality-check/)

16. **Apify Store actor developers** (scrapers sold per-result/per-event on a marketplace).
    - Apify says its most successful independent creators make over $10,000 MRR, but will not share names [platform claim]. — [Apify help](https://help.apify.com/en/articles/8684010-how-does-actor-monetization-work)
    - Apify paid out over $563,000 to community developers in September 2025 (stated as 6x the prior year). — [NatLawReview press release](https://natlawreview.com/press-releases/apify-bets-1m-independent-developers-building-ais-missing-tools)
    - Official commission is 20% on the rental model; payouts monthly, $20 minimum via PayPal/Wise. — [Apify docs](https://docs.apify.com/actors/monetize/monthly-payouts)

17. **The Odds API** (sports odds; 70+ sports, 40+ bookmakers; from $25/month with free tier). Revenue and founder details [NONE]. — [SourceForge](https://sourceforge.net/software/product/The-Odds-API/)

18. **Data Fetcher** (adjacent: an Airtable extension that pulls API data in, not a dataset seller). Solo founder Andy Cloak reports ~600 paying customers and ~$23K/month [F via Starter Story video]. — [Rosetta transcript](https://rosetta.to/u/starterstory/how-i-built-it-23k-month-micro-saas?t=0)

**C. Market intelligence, newsletters, consumer/prosumer data**

19. **Trends.vc** (paid market-trend reports + community; hand research; one person).
    - Launched February 2020; $0 revenue in March-April; first revenue May 2020; ~$24K in August 2020; $0 to $20K MRR in under a year; ~1,000 Pro members on 45-60K free subscribers; no sponsors by choice [F via Indie Hackers podcast/posts; figures are 2020-21, no current number found]. — [Indie Hackers podcast 173](https://www.indiehackers.com/podcast/173-dru-riley-of-trends-vc); [Indie Hackers post](https://www.indiehackers.com/post/growing-from-0-to-20k-mrr-with-winning-trends-dru-riley-bbc7ab2daa)

20. **Nomad List / Nomads** (crowd-sourced + scraped city data for remote workers; membership).
    - Founder said in 2017 revenue was $20-40K/month; a May 2025 Starter Story listing shows ~$16K/month [3P]; Latka/ZoomInfo's $5.3M/year is an estimate and conflicts sharply [EST]. — [Indie Hackers](https://www.indiehackers.com/post/founders-story-the-person-behind-nomad-list-7818b56ee7); [Starter Story](https://www.starterstory.com/stories/nomad-list-breakdown); [Latka](https://getlatka.com/companies/nomad-list)

21. **Exploding Topics** (trend detection from search/social signals). Acquired by Semrush (reported August 2024), terms undisclosed, revenue [NONE]. — [DesignRush](https://news.designrush.com/semrush-buys-exploding-topics-to-strengthen-market-research-capabilities)

22. **Klooks** (cleaned Brazilian private-company financial data sold to large firms). Founder said it broke $500,000 revenue in 2023 [F via interview]. — [Founderpath](https://founderpath.com/resources/alexandre-abu-jamra-klooks-brazilian-private-company-data/watch)

23. **Quiver Quantitative** (alternative data for retail investors — congressional trades etc.; two brothers, founded 2020). ~$2M ARR as of mid-2025 per one profile; raised a $2M seed in 2022, so not bootstrapped [3P]. — [CB Insights](https://www.cbinsights.com/company/quiver-quantitative)

24. **Keepa** (Amazon price history; Keepa GmbH, Germany; €29/month). No reliable revenue; a ~$400K/month figure is a formula-based extension-directory guess [EST — unreliable]. — [RevenueGeeks](https://revenuegeeks.com/software/keepa)

**D. Reference points that are NOT solo-replicable (venture-funded)**

25. **Shovels** (US building-permit data API). Founder disclosed ~$6K ARR in August 2023; Sacra/ARR.club estimate ~$1.5M end-2025 and ~$3M by August 2026; raised $5M seed (total reported $8.3M) [EST for later figures]. — [Sacra](https://sacra.com/c/shovels/); [ARR.club](https://www.arr.club/shovels/shovels-arr-hits-3m-after-3-years-of-growth)
26. **HigherGov** (government contract data from 200+ sources, founded 2022); PitchBook lists an acquisition on 20 May 2026 by Procurement Sciences AI [unverified by a second source]; revenue [NONE]. — [PitchBook](https://pitchbook.com/profiles/company/503735-32)
27. **Instrumentl** (grant database): YC S2016, founders were scientists who had built personal grant spreadsheets; now ~60 staff. Not bootstrapped; early revenue [NONE]. — [YC blog](https://www.ycombinator.com/blog/instrumentl)

### Inferences
- The highest-revenue solo-origin cases (BuiltWith, IPinfo, EODHD, SerpApi) all started 2008-2017 and compounded for 8+ years; cases started 2023-2025 with founder-stated numbers sit at $1.5K-$20K/month. Survivorship bias is heavy in the older set.
- Every case above $1M/year sells to businesses with a revenue-linked use (sales prospecting, product infrastructure, trading). The consumer/prosumer cases are either old (Nomad List) or lack figures (Keepa).
- Several winners were by-products of the founder's own need (Store Leads from promoting a Shopify app; Who Sponsors Stuff from an ad-sales prospecting sheet; Instrumentl from grant spreadsheets; Listen Notes from the founder's own listening). The dataset already had one proven user before it was sold.

### Gaps
- Could not verify any figure through TrustMRR/Stripe; search returned only third-party TrustMRR scrapers, not category leaderboards. TrustMRR would need to be opened directly.
- No revenue found for: The Odds API, Financial Modeling Prep, RentCast, Keepa (reliable), Glimpse, Owler, SimilarTech, Polygon early days, People Data Labs early days, RapidAPI data-API sellers, SponsorGap, Store Leads (founder-stated), Listen Notes, Growth List.
- Acquire.com / Flippa / Empire Flippers listings for data businesses were not searched successfully — no listing-level multiples collected.
- Indie Hackers, Starter Story and several blogs were not fetchable in this session; team size, exact dates and time-to-first-revenue for several cases are therefore missing or taken from search snippets.

## What patterns separate winners from failures?

### Takeaway
The repeatable winning shape is "public-but-messy data, structured and kept fresh, sold to B2B buyers who use it to find customers or to feed a product", with distribution that does not depend on a single platform's goodwill. The repeatable failure shape is dependence on one hostile source (LinkedIn) or on a handful of whale customers.

### Cited Findings
- Lead-gen framing: Store Leads is positioned for outbound prospecting, and reviewers note buyers pair it with a contact-enrichment tool. — [TrendTrack review](https://www.trendtrack.io/blog-post/store-leads-review)
- Customer concentration is common in small data APIs: Scrape Creators' revenue reportedly comes mostly from ~12 heavy users; Podscan lost profitability when a single major customer churned. — [BetterLaunch](https://www.betterlaunch.co/playbooks/episodes/adrian-scrape-creators); [The Bootstrapped Founder](https://thebootstrappedfounder.com/when-profitability-disappears-a-podscan-reality-check/)
- Infrastructure cost can exceed revenue for "index everything" products: Podscan ran ~$30K/month expenses, cut to ~$10K, against ~$6K MRR. — [The Bootstrapped Founder](https://thebootstrappedfounder.com/when-profitability-disappears-a-podscan-reality-check/)
- Maintenance burden for small lead lists: VCbacked's founder spends ~70% of time updating the database for ~$1.5K/month. — [Starter Story](https://www.starterstory.com/stories/vcbacked)
- Source-platform dependence: ~50% of Proxycurl's revenue came from LinkedIn scraping, and the LinkedIn suit ended the business. — [founder shutdown post](https://nubela.co/blog/goodbye-proxycurl/)
- Marketplace dependence costs margin: Listen Notes left RapidAPI once the 20% cut became material; Apify takes 20% on rentals. — [Listen Notes blog](https://www.listennotes.com/blog/how-i-accidentally-built-an-api-business-46/); [Apify docs](https://docs.apify.com/actors/monetize/monthly-payouts)
- Programmatic SEO is the visible channel for funded-startup lists (dozens of "List of funded X startups (2026)" pages, with a free top-100 list gating a premium database). — [Growth List](https://growthlist.co/funded-startups/); [Fundraise Insider](https://fundraiseinsider.com/blog/cyber-security-startups/)
- Commoditisation: a competitor claims sports odds data is "nearly a commodity" given free tiers covering 350+ bookmakers (vendor marketing, treat as opinion). — [OddsPapi blog](https://oddspapi.io/blog/?p=2918)
- Solo founders dominate the low bracket: one scrape of ~4,500 Indie Hackers products found 62% of products in the $1K-$10K MRR bracket list a team of one (single author's analysis, self-reported data). — [dev.to analysis](https://dev.to/agenthustler/i-scraped-4500-indiehackers-products-heres-what-the-mrr-data-reveals-18ki)

### Inferences
- Price point predicts ceiling: the generic funded-startup lists ($1.5-2.5K/month) compete with many near-identical products; niche-specific prospecting data with no direct substitute (newsletter sponsors, e-commerce stores, tech stack) reached $100K-$1M+.
- API delivery to developers gives usage-based upside but whale concentration; dashboard/CSV delivery to sales teams gives flatter, seat-based revenue. Several winners offer both.
- Data assembled from many small public sources (store sites, permits, newsletters, RSS, IP measurements, government portals) is legally and operationally safer than data taken from one large platform with a legal department.
- Being the by-product of the founder's own workflow is a cheap validation signal that recurs in the winners.

### Gaps
- No quantitative comparison of API vs dashboard vs CSV revenue was found; the pattern is inferred from a small set.
- No sourced evidence on alert-style products (tender/RFP alerts, government-contract alerts) run by solo founders; search returned only funded players (GovTribe, HigherGov).

## Which business models reach first revenue fastest for a solo founder, and typical timelines?

### Takeaway
On the few dated cases found, a paid newsletter/report product and a scraping API both reached first revenue within about 1-3 months and $10-20K MRR within about 12 months; lead lists reach first revenue quickly but the cases found plateaued at low four figures per month.

### Cited Findings
- Paid research newsletter: Trends.vc launched February 2020, first revenue May 2020 (~3 months), ~$24K in August 2020. — [Indie Hackers post](https://www.indiehackers.com/post/growing-from-0-to-20k-mrr-with-winning-trends-dru-riley-bbc7ab2daa)
- Data API: Scrape Creators launched June 2024 and reached $10K+ MRR in ~12 months, covering most of the founder's bills by March 2025 (~9 months). — [Indie Hackers](https://www.indiehackers.com/post/6iF8SJRF4WpciDff9aYi)
- Monitoring + API: Podscan reached ~$1K MRR two months after launch but was at only ~$6K MRR about a year later. — [Bootstrapped Founder ep. 317](https://goodpods.com/podcasts/the-bootstrapped-founder-190792/317-podscan-2-months-and-1k-mrr-in-50662029); [The Bootstrapped Founder](https://thebootstrappedfounder.com/when-profitability-disappears-a-podscan-reality-check/)
- Database licence: Who Sponsors Stuff reportedly reached six-figure annual revenue within a year of starting in late 2021. — [Koerner Office ep. 060](https://metacast.app/podcast/the-koerner-office---business-ideas-and-small/lwDrEPcr/060-a-100k-year-no-code-sponsor-database/fYxTYwjk)
- Outbound works for B2B data: Proxycurl's founder says cold email took it to $1M ARR in 18 months. — [Indie Hackers](https://www.indiehackers.com/post/i-cold-emailed-our-way-to-1m-arr-in-18-months-heres-the-story-dc078b4321)
- Marketplace route: Apify pays from a $20 threshold monthly and ran usage rewards of $2 per monthly active user ($100-$2,000 per actor) in its November 2025-January 2026 challenge. — [Apify docs](https://docs.apify.com/actors/monetize/monthly-payouts); [Apify $1M Challenge](https://www.wearedevelopers.com/companies/4035-apify)
- Slow route: IPinfo's own blog notes a bootstrapped startup "could take years" before it becomes a business; IPinfo ran as a side project through two jobs. — [IPinfo blog](https://ipinfo.io/blog/bootstrapping-a-startup)

### Inferences
- Fastest to first dollar is probably a marketplace-listed scraper/actor or a manually curated list sold by outreach, because both skip building billing, docs and SEO; but neither has evidence of scaling without later owning the customer relationship.
- A realistic solo planning assumption from these cases: first revenue in 1-3 months, $1K MRR in 2-4 months, $10K MRR in about 12 months for a good outcome, with many products stalling at $1-3K.

### Gaps
- Time-to-first-revenue was not available for most cases (BuiltWith, Store Leads, EODHD, SerpApi, Listen Notes).
- No dated evidence for one-off report sales or alert subscriptions by solo founders.
- No named Apify developer with a dated earnings figure; the Apify blog case study could not be fetched.

## Notable failures and shutdowns, and why

### Takeaway
The clearest shutdown is Proxycurl (about $10M ARR, killed by a LinkedIn lawsuit in 2025). The SerpApi litigation shows that scraping public, non-personal search results has so far survived a DMCA attack, but the case is not finished. I found no named niche data business that closed specifically because LLMs replaced it.

### Cited Findings
- Proxycurl: LinkedIn sued in January 2025 alleging fake accounts were used to scrape member profiles; the founder said fighting was not viable, settled out of court, and the service ended 4 July 2025; the resolution required permanent deletion of the LinkedIn data. — [Social Media Today](https://www.socialmediatoday.com/news/linkedin-wins-legal-case-data-scrapers-proxycurl/756101/); [LinkedIn newsroom](https://news.linkedin.com/2025/LinkedInWinsLegalBattleToProtectMemberData); [founder post](https://nubela.co/blog/goodbye-proxycurl/)
- Sources disagree on the aftermath: one says the founder sold Proxycurl to a competitor and now runs NinjaPear; another says it relaunched as Enrich Layer. — [founder blog](https://nubela.co/blog/what-is-proxycurl-api-now-in-2026-im-the-founder/); [StartupHub](https://www.startuphub.ai/ai-news/startup-news/2025/the-1-linkedin-scraping-startup-proxycurl-shuts-down)
- Google v. SerpApi: Google sued in December 2025 over scraping and circumvention; the court dismissed both DMCA claims on 20 July 2026, holding that blocking scrapers from public search results is not by itself copyright circumvention; Google filed an amended complaint on 10 August 2026 adding content-licensing terms. Outcome of the amended complaint not found. — [IPWatchdog](https://ipwatchdog.com/2025/12/26/google-sues-serpapi-parasitic-scraping-circumvention-protection-measures/); [Search Engine Land](https://searchengineland.com/google-loses-key-dmca-claims-against-serpapi-in-scraping-lawsuit-483185); [Search Engine Journal](https://www.searchenginejournal.com/google-amends-serpapi-suit-with-content-licensing-terms/)
- Reddit's separate DMCA suit against scrapers was allowed to proceed on 31 July (2026) in SDNY. — [Search Engine Journal](https://searchenginejournal.com/court-dismisses-googles-dmca-claims-against-serpapi/583033)
- Whale churn: Podscan's profitability lasted two months before a major customer left. — [The Bootstrapped Founder](https://thebootstrappedfounder.com/when-profitability-disappears-a-podscan-reality-check/)
- API-terms risk flows downstream too: Podscan's founder says he will turn off API access for anyone using it to build a competing service. — [Podscan directory entry / podcast](https://podnews.net/directory/company/podscan)
- Free-to-paid backlash creates openings: a dev.to post describes Wappalyzer "paywalling itself in 2023" and an open-source-powered replacement (vendor-authored). — [dev.to](https://dev.to/nexgendata/wappalyzer-paywalled-itself-in-2023-heres-the-oss-powered-replacement-3i01)
- Traffic-dependent small sites: Chartbeat data show search referrals to small publishers (1,000-10,000 daily page views) down 60% versus 22% for large ones; Google Search page views fell 34% from December 2024 to December 2025; ChatGPT referrals rose 200% but stayed under 1% of traffic. — [Axios, 17 March 2026](https://www.axios.com/2026/03/17/chartbeat-search-traffic-ai-chatbots); [Search Engine Land](https://searchengineland.com/small-publisher-search-traffic-drops-data-471974)

### Inferences
- Legal risk concentrates on personal data from a single platform accessed with logged-in/fake accounts. Public, non-personal, multi-source data has a materially better risk profile.
- The SerpApi ruling suggests that scraping plain public pages is defensible in the US for now, but the defendant needed the resources of a ~35-person profitable company to litigate; a solo founder would more likely fold as Proxycurl did.

### Gaps
- No founder post-mortem found for products killed by the Reddit or X/Twitter API price changes of 2023 (search did not surface them).
- No named data/directory business with revenue figures that shut down because of AI search.
- Outcome of Google's amended complaint against SerpApi unknown as of this research.

## How are LLMs and AI agents changing this in 2025-2026?

### Takeaway
Demand for fresh, structured web data delivered by API has risen sharply because AI products consume it, but the visible money has gone to funded search/crawl infrastructure where prices are falling fast; for solo developers, paid MCP servers and agent micropayments are technically available but I found no credible revenue evidence. Products whose distribution is organic search traffic to informational pages are the ones being squeezed.

### Cited Findings
- AI builders are now a major buyer of scraped data: ~40% of SerpApi's business comes from AI startups. — [The Information](https://feature.theinformation.com/newsletters/ai-agenda/meet-google-scraping-startup-used-chatgpt-cursor-perplexity); Sacra flags concentration in a few large AI customers as a risk. — [Sacra](https://sacra.com/c/serpapi/)
- Agent-search infrastructure grew very fast: Sacra estimates Exa at ~$14M annualised at end-2025 and ~$100M by September 2026 (CEO also announced passing $100M); Exa raised $250M at a $2.2B valuation in May 2026. — [Sacra](https://sacra.com/research/100m-year-google-for-ai-agents/); [Bloomberg](https://news.bgov.com/antitrust/andreessen-backed-ai-search-startup-exa-valued-at-2-2-billion)
- Tavily was acquired by Nebius for $275M, about 98x its 2025 revenue. — [Sacra](https://sacra.com/c/tavily/)
- Prices in that layer are collapsing: Perplexity and Parallel at $1 per 1,000 requests versus Exa at $4 and Tavily/You.com at $5. — [Sacra](https://sacra.com/research/100m-year-google-for-ai-agents/)
- Marketplace payouts to independent scraper developers grew ~6x year on year to $563K in September 2025, and Apify framed its $1M challenge around "AI's missing tools". — [NatLawReview press release](https://natlawreview.com/press-releases/apify-bets-1m-independent-developers-building-ais-missing-tools)
- Paid MCP tooling exists (Cloudflare `paidTool`, x402 micropayments in USDC), and builder commentary says the best candidates are servers offering data agents cannot get elsewhere, not thin wrappers on public APIs. — [Cloudflare docs](https://developers.cloudflare.com/agents/x402/charge-for-mcp-tools/); [dev.to state of MCP monetization](https://dev.to/kirothebot/the-state-of-mcp-monetization-in-2026-where-builders-actually-get-paid-34k9)
- Adoption figures for x402 conflict (50M+ transactions by early 2026 vs 165M across 69,000 agents attributed to Coinbase in April 2026); neither verified against a primary source. The claim that fewer than 5% of 14,000+ MCP servers are monetised is anecdotal. — [dev.to](https://dev.to/kirothebot/mcp-hit-9400-servers-in-17-months-the-payment-layer-is-still-missing-1kb5); [Eco guide](https://eco.com/support/en/articles/14846276)
- Incumbents are packaging data for agents: a Keepa MCP package exists on npm, IPinfo publishes an "information for AI" page, Listen Notes publishes llms-full.txt, and Apify lists actors with MCP endpoints. — [socket.dev keepa-mcp](https://socket.dev/npm/package/keepa-mcp); [IPinfo](https://ipinfo.io/information-for-ai); [Listen Notes](https://www.listennotes.com/llms-full.txt); [Apify](https://apify.com/automation-lab/trustmrr-startups-scraper/api/mcp)
- Search-traffic erosion for small sites (see Chartbeat figures above) hits SEO-dependent distribution. — [Axios](https://www.axios.com/2026/03/17/chartbeat-search-traffic-ai-chatbots)

### Inferences
- Being commoditised: generic web search/crawl-as-a-service (price war among funded players), generic "trend" and "list of funded startups" content that an LLM with search can assemble on demand, and anything distributed mainly through informational SEO pages.
- Gaining: narrow, hard-to-assemble, frequently changing datasets that a general web search cannot reproduce in one call (permits, store-level e-commerce attributes, sponsor relationships, IP ranges, transcripts) — exposed as API plus MCP so agent builders can buy them. The buyer shifts from a human in a dashboard to a developer wiring a tool into an agent.
- For a solo founder in late 2026, MCP is best treated as an extra delivery channel on top of a conventional subscription/API business, not as the business model: there is no evidence yet of meaningful solo MCP revenue.
- Whale concentration risk rises when AI companies are the customers (SerpApi, Scrape Creators pattern).

### Gaps
- No audited or founder-stated revenue for any solo-run paid MCP server.
- No direct evidence on whether Exploding Topics, Glimpse or similar trend tools lost revenue to LLMs.
- No data on how much of small data-API demand in 2026 originates from agents versus traditional software.
