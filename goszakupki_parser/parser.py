"""Парсер госзакупок с zakupki.gov.ru."""

import time
import httpx
from bs4 import BeautifulSoup
from config import HEADERS, ZAKUPKI_SEARCH_URL, REQUEST_DELAY, MAX_RETRIES, RESULTS_PER_PAGE


def search_tenders(query: str, fz: str = "44", pages: int = 1) -> list[dict]:
    """Поиск тендеров по ключевому слову.

    Args:
        query: Поисковый запрос (например, "разработка ПО")
        fz: Федеральный закон (44 или 223)
        pages: Количество страниц результатов

    Returns:
        Список тендеров с основной информацией
    """
    tenders = []

    for page in range(1, pages + 1):
        params = {
            "searchString": query,
            "morphology": "on",
            "search-filter": "Дата+размещения",
            "pageNumber": str(page),
            "sortDirection": "false",
            "recordsPerPage": str(RESULTS_PER_PAGE),
            "showLotsInfoHidden": "false",
            "fz44": "on" if fz == "44" else "",
            "fz223": "on" if fz == "223" else "",
            "af": "on",
            "ca": "on",
        }

        for attempt in range(MAX_RETRIES):
            try:
                with httpx.Client(headers=HEADERS, timeout=30.0) as client:
                    response = client.get(ZAKUPKI_SEARCH_URL, params=params)
                    response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")
                rows = soup.select(".search-registry-entry-block")

                for row in rows:
                    tender = _parse_tender_row(row)
                    if tender:
                        tenders.append(tender)

                break  # Успешный запрос
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                print(f"Ошибка запроса (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(REQUEST_DELAY * (attempt + 1))

        time.sleep(REQUEST_DELAY)

    return tenders


def _parse_tender_row(row) -> dict | None:
    """Парсинг одной строки результатов поиска."""
    try:
        # Номер закупки
        number_el = row.select_one(".registry-entry__header-mid__number a")
        number = number_el.get_text(strip=True) if number_el else ""
        link = number_el.get("href", "") if number_el else ""

        # Название
        name_el = row.select_one(".registry-entry__body-value")
        name = name_el.get_text(strip=True) if name_el else ""

        # Цена
        price_el = row.select_one(".price-block__value")
        price = price_el.get_text(strip=True) if price_el else ""

        # Заказчик
        org_el = row.select_one(".registry-entry__body-href a")
        organization = org_el.get_text(strip=True) if org_el else ""

        # Даты
        dates = row.select(".data-block__value")
        date_published = dates[0].get_text(strip=True) if len(dates) > 0 else ""
        date_deadline = dates[1].get_text(strip=True) if len(dates) > 1 else ""

        return {
            "number": number,
            "name": name,
            "price": price,
            "organization": organization,
            "date_published": date_published,
            "date_deadline": date_deadline,
            "link": f"https://zakupki.gov.ru{link}" if link and not link.startswith("http") else link,
        }
    except Exception as e:
        print(f"Ошибка парсинга строки: {e}")
        return None


def get_tender_details(tender_url: str) -> dict:
    """Получение детальной информации о тендере."""
    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(headers=HEADERS, timeout=30.0) as client:
                response = client.get(tender_url)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            details = {
                "url": tender_url,
                "documents": [],
                "lots": [],
            }

            # Документы
            doc_links = soup.select(".attachment__value a")
            for doc in doc_links:
                details["documents"].append({
                    "name": doc.get_text(strip=True),
                    "url": doc.get("href", ""),
                })

            # Лоты
            lot_rows = soup.select(".blockInfo__section")
            for lot in lot_rows:
                lot_name = lot.select_one(".section__title")
                lot_price = lot.select_one(".cost")
                if lot_name:
                    details["lots"].append({
                        "name": lot_name.get_text(strip=True),
                        "price": lot_price.get_text(strip=True) if lot_price else "",
                    })

            return details
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            print(f"Ошибка запроса деталей (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * (attempt + 1))

    return {}
