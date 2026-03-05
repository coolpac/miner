"""Business entity & UCC filing lookup across multiple sources."""

import time

import httpx

from config import (
    HEADERS, REQUEST_DELAY, MAX_RETRIES,
    OPENCORPORATES_API_URL, OPENCORPORATES_API_KEY,
    SEC_COMPANY_TICKERS, SEC_HEADERS,
    UK_COMPANIES_HOUSE_URL, UK_COMPANIES_HOUSE_KEY,
)


# --- OpenCorporates (global, 200M+ companies) ---

def search_opencorporates(
    query: str,
    jurisdiction: str = "us",
    per_page: int = 30,
) -> list[dict]:
    """Search companies via OpenCorporates API.

    Args:
        query: Company name to search.
        jurisdiction: Country code (us, gb, de, fr, etc.) or state (us_ca, us_ny).
        per_page: Results per page (max 100).

    Returns:
        List of company records.
    """
    url = f"{OPENCORPORATES_API_URL}/companies/search"
    params = {
        "q": query,
        "jurisdiction_code": jurisdiction,
        "per_page": str(per_page),
        "order": "score",
    }
    if OPENCORPORATES_API_KEY:
        params["api_token"] = OPENCORPORATES_API_KEY

    data = _get_json(url, params)
    if not data:
        return []

    companies = data.get("results", {}).get("companies", [])
    return [_normalize_oc_company(c.get("company", {})) for c in companies]


def get_opencorporates_company(jurisdiction: str, company_number: str) -> dict | None:
    """Get company details by jurisdiction and number.

    Args:
        jurisdiction: e.g., "us_ca", "gb"
        company_number: Company registration number
    """
    url = f"{OPENCORPORATES_API_URL}/companies/{jurisdiction}/{company_number}"
    params = {}
    if OPENCORPORATES_API_KEY:
        params["api_token"] = OPENCORPORATES_API_KEY

    data = _get_json(url, params)
    if not data:
        return None

    company = data.get("results", {}).get("company", {})
    return _normalize_oc_company(company)


def _normalize_oc_company(c: dict) -> dict:
    return {
        "source": "opencorporates",
        "name": c.get("name", ""),
        "company_number": c.get("company_number", ""),
        "jurisdiction": c.get("jurisdiction_code", ""),
        "status": c.get("current_status", ""),
        "type": c.get("company_type", ""),
        "incorporation_date": c.get("incorporation_date", ""),
        "dissolution_date": c.get("dissolution_date", ""),
        "address": c.get("registered_address_in_full", ""),
        "agent": c.get("agent_name", ""),
        "url": c.get("opencorporates_url", ""),
        "registry_url": c.get("registry_url", ""),
    }


# --- SEC EDGAR (US public companies) ---

def search_sec_companies(query: str) -> list[dict]:
    """Search US public companies via SEC EDGAR.

    Args:
        query: Company name or ticker.

    Returns:
        List of company records with CIK, ticker, and name.
    """
    data = _get_json(SEC_COMPANY_TICKERS, {}, headers=SEC_HEADERS)
    if not data:
        return []

    query_lower = query.lower()
    results = []
    for entry in data.values():
        name = entry.get("title", "")
        ticker = entry.get("ticker", "")
        if query_lower in name.lower() or query_lower in ticker.lower():
            results.append({
                "source": "sec_edgar",
                "cik": str(entry.get("cik_str", "")),
                "ticker": ticker,
                "name": name,
                "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={entry.get('cik_str', '')}&type=&dateb=&owner=include&count=40",
            })

    return results[:50]


def get_sec_filings(cik: str, filing_type: str = "10-K", count: int = 10) -> list[dict]:
    """Get recent SEC filings for a company by CIK.

    Args:
        cik: Central Index Key (SEC identifier).
        filing_type: Filing type (10-K, 10-Q, 8-K, etc.).
        count: Number of filings to return.
    """
    # Zero-pad CIK to 10 digits
    cik_padded = cik.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

    data = _get_json(url, {}, headers=SEC_HEADERS)
    if not data:
        return []

    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    filings = []
    for i in range(len(forms)):
        if filing_type and forms[i] != filing_type:
            continue
        accession = accessions[i].replace("-", "")
        filings.append({
            "form": forms[i],
            "date": dates[i],
            "accession": accessions[i],
            "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_docs[i]}",
        })
        if len(filings) >= count:
            break

    return filings


# --- UK Companies House ---

def search_uk_companies(query: str, items_per_page: int = 20) -> list[dict]:
    """Search UK companies via Companies House API.

    Requires API key from https://developer.company-information.service.gov.uk/
    """
    if not UK_COMPANIES_HOUSE_KEY:
        print("UK Companies House API key not configured. Set UK_COMPANIES_HOUSE_KEY in config.py")
        return []

    url = f"{UK_COMPANIES_HOUSE_URL}/search/companies"
    params = {"q": query, "items_per_page": str(items_per_page)}
    headers = {**HEADERS, "Accept": "application/json"}

    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    url, params=params, headers=headers,
                    auth=(UK_COMPANIES_HOUSE_KEY, ""),
                )
                response.raise_for_status()
                data = response.json()

            items = data.get("items", [])
            return [{
                "source": "uk_companies_house",
                "name": item.get("title", ""),
                "company_number": item.get("company_number", ""),
                "status": item.get("company_status", ""),
                "type": item.get("company_type", ""),
                "address": item.get("address_snippet", ""),
                "incorporation_date": item.get("date_of_creation", ""),
                "dissolution_date": item.get("date_of_cessation", ""),
                "url": f"https://find-and-update.company-information.service.gov.uk/company/{item.get('company_number', '')}",
            } for item in items]

        except (httpx.HTTPError, httpx.TimeoutException) as e:
            print(f"UK Companies House error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * (attempt + 1))

    return []


# --- Helpers ---

def _get_json(url: str, params: dict, headers: dict | None = None) -> dict | None:
    """Fetch JSON from URL with retries."""
    headers = headers or {**HEADERS, "Accept": "application/json"}

    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(headers=headers, timeout=30.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            print(f"Request error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * (attempt + 1))

    return None
