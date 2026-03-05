# Data Mining Toolkit

Collection of scrapers and tools for aggregating public data from US & EU government sources.

> **[Monetization Plan](PLAN.md)** — strategy for building API services on top of fragmented public data.

## Tools

### 1. [Permit Scraper](permit_scraper/) — US Building Permits
Scrapes building permit data from 10+ major US cities via Socrata Open Data APIs. Normalizes data into a common schema.

```bash
cd permit_scraper
pip install -r requirements.txt
python main.py fetch new_york_city --days 7 --limit 100
python main.py fetch-all --days 14
python main.py stats chicago --days 30
python main.py cities
```

### 2. [SOS/SEC Lookup](sec_state_lookup/) — US/UK Business Entity Search
Search companies across OpenCorporates (200M+ companies, 140+ jurisdictions), SEC EDGAR (US public companies), and UK Companies House.

```bash
cd sec_state_lookup
pip install -r requirements.txt
python main.py search "Tesla" --source all
python main.py search "Google" --jurisdiction us_ca
python main.py filings 0001318605 --type 10-K --count 5
python main.py company us_ca C0806592
```

### 3. [EU Tenders](eu_tenders/) — EU Public Procurement (TED)
Parse and monitor EU-wide public procurement notices from TED (Tenders Electronic Daily). Filter by CPV category, country, and keywords.

```bash
cd eu_tenders
pip install -r requirements.txt
python main.py search "software development" --country DE --days 14
python main.py search --cpv it_services --country FR
python main.py monitor --cpv 72000000 --country DE --interval 1800
python main.py categories
```

### 4. [WB Parser](wb_parser/) — Wildberries Product Scraper
Product, price, stock and review scraper for Wildberries marketplace. Export to Excel/CSV.

```bash
cd wb_parser
pip install -r requirements.txt
python main.py search "кроссовки" --pages 5
```

### 5. [FunPay Tools](funpay_tools/) — FunPay Marketplace Tools
Lot parsing, price monitoring, and arbitrage tools for FunPay.
