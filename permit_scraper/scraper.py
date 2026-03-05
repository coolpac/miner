"""US Building Permit Scraper using Socrata Open Data API (SODA)."""

import time
from datetime import datetime, timedelta

import httpx

from config import HEADERS, PERMIT_SOURCES, REQUEST_DELAY, MAX_RETRIES


def fetch_permits(
    city: str,
    limit: int = 1000,
    offset: int = 0,
    days_back: int = 30,
    permit_type: str | None = None,
    app_token: str | None = None,
) -> list[dict]:
    """Fetch building permits from a city's open data portal.

    Args:
        city: City key from PERMIT_SOURCES config.
        limit: Max records to return (Socrata max is usually 50,000).
        offset: Pagination offset.
        days_back: Only fetch permits issued in the last N days.
        permit_type: Filter by permit type (optional).
        app_token: Socrata app token for higher rate limits (optional).

    Returns:
        List of permit records.
    """
    source = PERMIT_SOURCES.get(city)
    if not source:
        print(f"Unknown city: {city}. Available: {', '.join(PERMIT_SOURCES.keys())}")
        return []

    if source["api_type"] == "socrata":
        return _fetch_socrata(source, limit, offset, days_back, permit_type, app_token)

    print(f"Unsupported API type: {source['api_type']}")
    return []


def _fetch_socrata(
    source: dict,
    limit: int,
    offset: int,
    days_back: int,
    permit_type: str | None,
    app_token: str | None,
) -> list[dict]:
    """Fetch from Socrata SODA API."""
    domain = source["domain"]
    dataset_id = source["dataset_id"]
    url = f"https://{domain}/resource/{dataset_id}.json"

    # Build SoQL query
    since_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00")

    params = {
        "$limit": str(limit),
        "$offset": str(offset),
        "$order": ":id",
    }

    # Add date filter — field names vary by dataset
    # Common field names: issued_date, issue_date, permit_issue_date, issueddate
    where_clauses = []
    date_fields = [
        "issued_date", "issue_date", "permit_issue_date",
        "issueddate", "permit_issuance_date", "issuancedate",
    ]
    # We try a generic approach; in production, map per dataset
    where_clauses.append(f"issueddate >= '{since_date}' OR issued_date >= '{since_date}'")

    if permit_type:
        where_clauses.append(f"upper(permit_type) LIKE '%{permit_type.upper()}%'")

    if where_clauses:
        params["$where"] = " AND ".join(f"({c})" for c in where_clauses)

    if app_token:
        params["$$app_token"] = app_token

    headers = {**HEADERS, "Accept": "application/json"}

    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(headers=headers, timeout=30.0) as client:
                response = client.get(url, params=params)

                if response.status_code == 400:
                    # Date field name mismatch — retry without date filter
                    params.pop("$where", None)
                    response = client.get(url, params=params)

                response.raise_for_status()
                records = response.json()

                return [_normalize_permit(r, source) for r in records]

        except (httpx.HTTPError, httpx.TimeoutException) as e:
            print(f"Error fetching {source['name']} (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * (attempt + 1))

    return []


def _normalize_permit(record: dict, source: dict) -> dict:
    """Normalize permit record to a common schema."""
    # Map various field names to our standard schema
    def get_first(*keys):
        for k in keys:
            val = record.get(k) or record.get(k.lower()) or record.get(k.upper())
            if val:
                return str(val).strip()
        return ""

    return {
        "source_city": source["name"],
        "source_state": source["state"],
        "permit_number": get_first(
            "permit_number", "permit_no", "permitnumber", "job__",
            "permit_num", "application_number", "record_id",
        ),
        "permit_type": get_first(
            "permit_type", "permittype", "permit_type_mapped",
            "work_type", "type", "permit_category",
        ),
        "description": get_first(
            "job_description", "description", "permit_description",
            "work_description", "project_description", "scope_of_work",
        ),
        "status": get_first(
            "permit_status", "status", "current_status",
            "permit_status_mapped",
        ),
        "issued_date": get_first(
            "issued_date", "issueddate", "issue_date",
            "permit_issue_date", "issuancedate", "permit_issuance_date",
        ),
        "address": get_first(
            "address", "street_address", "location",
            "house__", "street_name", "site_address",
        ),
        "owner": get_first(
            "owner_s_business_name", "owner_name", "owner",
            "applicant_name", "applicant",
        ),
        "contractor": get_first(
            "contractor_name", "contractor", "contractor_s_business_name",
            "general_contractor",
        ),
        "estimated_cost": get_first(
            "estimated_cost", "job_value", "valuation",
            "permit_value", "construction_cost", "total_project_valuation",
        ),
        "latitude": get_first("latitude", "lat"),
        "longitude": get_first("longitude", "lng", "lon"),
        "raw": record,  # keep original for debugging
    }


def fetch_all_cities(
    days_back: int = 30,
    limit_per_city: int = 500,
    app_token: str | None = None,
) -> dict[str, list[dict]]:
    """Fetch recent permits from all configured cities.

    Returns:
        Dict of {city_key: [permits]}
    """
    all_permits = {}

    for city_key, source in PERMIT_SOURCES.items():
        print(f"Fetching: {source['name']}, {source['state']}...")
        permits = fetch_permits(
            city_key,
            limit=limit_per_city,
            days_back=days_back,
            app_token=app_token,
        )
        all_permits[city_key] = permits
        print(f"  → {len(permits)} permits")
        time.sleep(REQUEST_DELAY)

    total = sum(len(p) for p in all_permits.values())
    print(f"\nTotal: {total} permits from {len(all_permits)} cities")
    return all_permits
