# Public Data Monetization Plan (US & EU)

## Concept

Build API services and scraping tools that aggregate fragmented public data from US and EU government sources, normalize it, and sell structured access via API/subscription.

**Core arbitrage:** Data is public but locked in thousands of local jurisdictions with no unified format. We aggregate, normalize, and serve it via developer-friendly APIs.

---

## Top Niches (ranked by demand × access difficulty × lack of competition)

### 1. Restaurant Health Inspections — NO dominant player
- **What:** Aggregate health inspection scores/violations from all US county health departments
- **Why:** Data spread across 3,100+ county portals, each with different format. No single API exists.
- **Source sites:** Each county health dept (e.g., NYC DOHMH, LA County, etc.) + AFDO directory
- **Buyers:** Restaurant investors ($100-500/mo), commercial RE brokers, insurance underwriters, food safety platforms
- **Pricing model:** $200-500/mo subscription, or $0.10-0.50/lookup
- **Competition:** Virtually none (HDScores, SafeEats — small apps, limited coverage)
- **Revenue potential:** $50K-200K/yr ARR within 12 months

### 2. Contractor License Verification — early market
- **What:** Unified API to verify contractor licenses across all 50 US states
- **Why:** Each state has its own licensing board portal, no federal standard
- **Buyers:** Insurance companies, general contractors, platforms like Angi/HomeAdvisor
- **Pricing:** ~$0.75/lookup (benchmark: Cobalt Intelligence)
- **Competition:** Cobalt Intelligence (starting to cover, but early stage)

### 3. Code Violations & Citations — zero aggregator exists
- **What:** Building code violations, fire code violations, environmental citations
- **Why:** Data only at municipal code enforcement level, no aggregator
- **Buyers:** RE investors (find distressed properties), insurance underwriters, tenant screening
- **Pricing:** $300-600/mo or per-lookup
- **Competition:** None

### 4. State Court Records — barely digitized
- **What:** Digitize and structure state-level court dockets (not federal PACER)
- **Why:** Many state courts still paper-based or PDF-only. PACER charges $0.10/page.
- **Buyers:** Law firms ($5K-50K/yr), litigation finance funds, insurance companies
- **Competition:** UniCourt ($49-299/mo), Trellis (limited coverage), CourtListener (free/open source)

### 5. UCC Filings & Business Entity Data — fragmented across 50 states
- **What:** Unified search for Secretary of State filings, UCC liens, corporate registrations
- **Why:** Average US score for company data openness is only 31/100 (OpenCorporates). Each state portal has different format.
- **Buyers:** Fintechs/lenders (KYB/KYC), banks, law firms doing due diligence
- **Pricing:** $0.75-2.00/lookup
- **Competition:** Cobalt Intelligence, Middesk (enterprise), D&B ($25K+/yr)

### 6. Building Permits — proven market, room for budget player
- **What:** New construction permits by geography, permit type, contractor
- **Why:** Thousands of individual city/county portals
- **Buyers:** Building material suppliers ($500-2K/mo), subcontractors ($200-600/mo), RE developers
- **Competition:** Shovels.ai ($599/mo), BuildZoom, Construction Monitor — but expensive

---

## EU-Specific Opportunities

### Company Registries
- **UK:** Companies House API (free but rate-limited, value in enrichment)
- **Germany:** Handelsregister (notoriously hard to access programmatically)
- **France:** INSEE/SIRENE (open data but needs normalization)
- **Pan-EU:** No single API covers all 27 member states + UK
- **Existing:** OpenCorporates (200M+ companies, 140+ jurisdictions), Global Database

### EU Public Procurement (TED — Tenders Electronic Daily)
- **What:** EU-wide tenders above threshold values (~€140K for services)
- **Source:** ted.europa.eu — structured XML but complex to parse
- **Buyers:** Contractors, consultancies, sales teams targeting government contracts
- **Pricing:** $300-1,000/mo for filtered, enriched feeds

### GDPR-Adjacent: Data Protection Fines & Decisions
- **What:** Aggregate DPA decisions across all EU member states
- **Buyers:** Compliance officers, law firms, DPOs
- **Source:** Each national DPA website (CNIL, ICO, BfDI, etc.)

---

## Competitive Landscape & Pricing

| Provider | Niche | Pricing |
|----------|-------|---------|
| Cobalt Intelligence | SOS + UCC lookups | ~$0.75/lookup at 1K/mo |
| UniCourt | Court records/analytics | $49-299/mo, Enterprise API custom |
| Shovels.ai | Building permits | Starting $599/mo |
| RentCast | Property data | Free (50 calls/mo) → $0.015/req |
| ATTOM Data | Property/permit data | ~$95-500+/mo API |
| BuildZoom Data | 350M+ permits | Enterprise (contact sales) |
| D&B Direct+ | Business entity data | ~$25K+/yr |
| OpenCorporates | Global company data | Free tier + paid API |
| Middesk | UCC + KYB | Enterprise pricing |
| Trellis | State trial court analytics | Contact sales |

---

## Buyer Personas & Budgets

| Persona | Data Need | Pain Point | Budget |
|---------|-----------|-----------|--------|
| **Fintech underwriter** | SOS filings, UCC liens, judgments | Manual 50-state searches, $2-5/lookup from legacy providers | $10K-100K+/yr |
| **Commercial RE analyst** | Zoning, permits, property records | Calling county offices, reading zoning PDFs | $5K-25K/yr |
| **Building material sales rep** | New permits by geography | County newsletters, driving around | $500-2K/mo |
| **Electrical/plumbing sub** | Permits by type in service area | Word of mouth, cold calling GCs | $200-600/mo |
| **Insurance underwriter** | Claims, property risk, contractor license | $10-50/report from legacy providers | $25K-200K+/yr |
| **Bank compliance officer** | KYB, beneficial ownership, sanctions | D&B at $25K+/yr, manual verification | $25K-500K/yr |
| **Litigation finance fund** | Court dockets, outcomes, judge analytics | PACER at $0.10/page + manual analysis | $50K-200K/yr |
| **Restaurant franchise investor** | Health inspections, violations, new licenses | Manually checking county websites | $100-500/mo |

---

## Technical Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  Scrapers/ETL   │────▶│  Database    │────▶│  REST API   │
│  (Python)       │     │  (PostgreSQL) │     │  (FastAPI)  │
│                 │     │              │     │             │
│ • County sites  │     │ • Raw data   │     │ • Auth/Keys │
│ • State portals │     │ • Normalized │     │ • Rate limit│
│ • PDF parsers   │     │ • Indexed    │     │ • Billing   │
│ • EU TED/APIs   │     │              │     │ • Docs      │
└─────────────────┘     └──────────────┘     └─────────────┘
```

### Stack
- **Scraping:** Python (httpx, BeautifulSoup, Playwright for JS-heavy sites)
- **PDF parsing:** pdfplumber, camelot-py
- **Database:** PostgreSQL + Redis (cache)
- **API:** FastAPI
- **Deploy:** Docker, Railway/Fly.io
- **Monitoring:** Scrapy-style logs, alerts on parser breakage
- **Billing:** Stripe

---

## Action Plan

### Phase 1 — MVP (2-4 weeks)
- [ ] Pick 1 niche to start (recommendation: **US building permits** — proven demand, clear monetization)
- [ ] Build scrapers for top 20 US cities/counties by population
- [ ] Create PostgreSQL schema for normalized permit data
- [ ] Stand up FastAPI with API key auth
- [ ] Deploy MVP, get first 5 beta users

### Phase 2 — Expand Coverage (1-2 months)
- [ ] Scale to 100+ jurisdictions
- [ ] Add scheduled scraping (cron/Celery)
- [ ] Integrate Stripe billing
- [ ] Write API documentation (OpenAPI/Swagger)
- [ ] Launch landing page
- [ ] Add 2nd data vertical (UCC filings or health inspections)

### Phase 3 — Scale (3-6 months)
- [ ] Expand to EU markets (TED procurement, company registries)
- [ ] Add webhook notifications for data changes
- [ ] Enterprise tiers with SLA
- [ ] Partner integrations (Zapier, CRM connectors)

---

## Quick Wins (start now)

1. **permit_scraper** — US building permit data from top cities → sell as API
2. **sec_state_lookup** — Secretary of State + UCC filing search across states
3. **eu_tenders** — EU TED procurement data parser/monitor
4. **health_inspections** — Restaurant inspection scores aggregator (biggest gap)
