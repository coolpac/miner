"""EU TED (Tenders Electronic Daily) parser.

Uses the TED API v3 to search and fetch EU public procurement notices.
TED publishes all EU tenders above threshold values (~EUR 140K for services).
"""

import time
from datetime import datetime, timedelta

import httpx

from config import HEADERS, TED_SEARCH_URL, REQUEST_DELAY, MAX_RETRIES, RESULTS_PER_PAGE


def search_tenders(
    query: str = "",
    cpv: str = "",
    country: str = "",
    days_back: int = 30,
    page: int = 1,
    limit: int = RESULTS_PER_PAGE,
) -> dict:
    """Search EU tenders via TED API.

    Args:
        query: Free text search.
        cpv: CPV code (e.g., "72000000" for IT services).
        country: ISO country code (e.g., "DE", "FR").
        days_back: Only show tenders published in last N days.
        page: Page number.
        limit: Results per page.

    Returns:
        Dict with 'total', 'tenders' list.
    """
    since_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")

    # Build TED query
    query_parts = []
    if query:
        query_parts.append(f'TD=[{query}]')
    if cpv:
        query_parts.append(f'PC=[{cpv}]')
    if country:
        query_parts.append(f'CY=[{country}]')
    query_parts.append(f'PD>=[{since_date}]')

    ted_query = " AND ".join(query_parts)

    payload = {
        "q": ted_query,
        "pageNum": page,
        "pageSize": limit,
        "scope": "3",  # All notices
        "sortField": "PD",
        "sortOrder": "desc",
    }

    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(headers=HEADERS, timeout=30.0) as client:
                response = client.post(TED_SEARCH_URL, json=payload)
                response.raise_for_status()
                data = response.json()

            notices = data.get("notices", data.get("results", []))
            total = data.get("total", len(notices))

            tenders = [_normalize_notice(n) for n in notices]
            return {"total": total, "tenders": tenders}

        except (httpx.HTTPError, httpx.TimeoutException) as e:
            print(f"TED API error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * (attempt + 1))

    return {"total": 0, "tenders": []}


def _normalize_notice(notice: dict) -> dict:
    """Normalize TED notice to common format."""
    # TED API response structure varies; handle multiple formats
    content = notice.get("content", notice)

    def get(*keys):
        for k in keys:
            val = content.get(k) or notice.get(k)
            if val:
                return str(val).strip() if not isinstance(val, dict) else val
        return ""

    # Extract value
    value = ""
    value_data = get("estimatedValue", "value", "totalValue")
    if isinstance(value_data, dict):
        amount = value_data.get("amount", "")
        currency = value_data.get("currency", "EUR")
        value = f"{amount} {currency}" if amount else ""
    elif value_data:
        value = str(value_data)

    return {
        "notice_id": get("noticeId", "tedNoticeId", "docId"),
        "title": get("title", "titleText"),
        "description": get("shortDescription", "description", "descriptionText"),
        "buyer": get("buyerName", "organisationName", "contractingBody"),
        "country": get("countryCode", "country", "isoCountry"),
        "cpv": get("cpvCode", "mainCpv"),
        "value": value,
        "publication_date": get("publicationDate", "datePublished"),
        "deadline": get("deadlineDate", "deadline", "timeLimit"),
        "notice_type": get("noticeType", "type"),
        "url": f"https://ted.europa.eu/en/notice/-/{get('noticeId', 'tedNoticeId', 'docId')}" if get("noticeId", "tedNoticeId", "docId") else "",
    }


def get_notice_details(notice_id: str) -> dict | None:
    """Get full details of a TED notice.

    Args:
        notice_id: TED notice ID (e.g., "2024/S 001-000001")
    """
    url = f"https://api.ted.europa.eu/v3/notices/{notice_id}"

    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(headers=HEADERS, timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            print(f"TED detail error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * (attempt + 1))

    return None


def monitor_new_tenders(
    cpv: str = "",
    country: str = "",
    interval_seconds: int = 3600,
):
    """Continuously monitor for new tenders matching criteria.

    Args:
        cpv: CPV code to filter.
        country: Country code to filter.
        interval_seconds: Check interval.
    """
    seen_ids = set()

    print(f"Monitoring TED tenders (CPV: {cpv or 'all'}, Country: {country or 'all'})")
    print(f"Check interval: {interval_seconds}s. Press Ctrl+C to stop.\n")

    try:
        while True:
            result = search_tenders(cpv=cpv, country=country, days_back=1, limit=50)
            new_tenders = [
                t for t in result["tenders"]
                if t["notice_id"] and t["notice_id"] not in seen_ids
            ]

            for t in new_tenders:
                seen_ids.add(t["notice_id"])
                print(f"[NEW] {t['notice_id']} | {t['country']} | {t['value']}")
                print(f"      {t['title'][:100]}")
                print(f"      Buyer: {t['buyer'][:80]}")
                print(f"      Deadline: {t['deadline']}")
                print()

            if not new_tenders:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No new tenders")

            print(f"Next check in {interval_seconds}s...\n")
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print(f"\nStopped. Total unique tenders seen: {len(seen_ids)}")
