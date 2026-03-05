"""Configuration for US Secretary of State & UCC Filing Lookup."""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_DELAY = 2.0
MAX_RETRIES = 3

# OpenCorporates API (free tier: 50 requests/day, with API key: 500/day)
OPENCORPORATES_API_URL = "https://api.opencorporates.com/v0.4"
OPENCORPORATES_API_KEY = ""  # Get from https://opencorporates.com/api_accounts/new

# SEC EDGAR (free, rate limit: 10 requests/sec)
SEC_EDGAR_API_URL = "https://efts.sec.gov/LATEST/search-index"
SEC_EDGAR_COMPANY_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
SEC_FULL_TEXT_SEARCH = "https://efts.sec.gov/LATEST/search-index"
SEC_COMPANY_TICKERS = "https://www.sec.gov/files/company_tickers.json"

# SEC EDGAR requires User-Agent with contact info
SEC_HEADERS = {
    "User-Agent": "DataMiner contact@example.com",
    "Accept": "application/json",
}

# States with known open data APIs for business entities
STATE_APIS = {
    "CA": {
        "name": "California",
        "search_url": "https://bizfileonline.sos.ca.gov/search/business",
        "api_type": "web_scrape",
    },
    "FL": {
        "name": "Florida (SunBiz)",
        "search_url": "https://search.sunbiz.org/Inquiry/CorporationSearch/ByName",
        "api_type": "web_scrape",
    },
    "NY": {
        "name": "New York",
        "search_url": "https://appext20.dos.ny.gov/corp_public/CORPSEARCH.ENTITY_SEARCH_ENTRY",
        "api_type": "web_scrape",
    },
    "TX": {
        "name": "Texas",
        "search_url": "https://mycpa.cpa.state.tx.us/coa/",
        "api_type": "web_scrape",
    },
    "DE": {
        "name": "Delaware",
        "search_url": "https://icis.corp.delaware.gov/ecorp/entitysearch/namesearch.aspx",
        "api_type": "web_scrape",
        "note": "Delaware charges $10-20/lookup for detailed records",
    },
}

# UK Companies House (free API, 600 requests/5 min)
UK_COMPANIES_HOUSE_URL = "https://api.company-information.service.gov.uk"
UK_COMPANIES_HOUSE_KEY = ""  # Get from https://developer.company-information.service.gov.uk/

OUTPUT_DIR = "output"
