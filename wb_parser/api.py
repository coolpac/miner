"""Модуль для работы с API Wildberries."""

import time
import requests
from typing import Optional
from config import (
    SEARCH_URL, CARD_DETAIL_URL, FEEDBACKS_URL, SALES_URL,
    CATALOG_MENU_URL, HEADERS, DEFAULT_DEST, DEFAULT_CURRENCY,
    DEFAULT_SPP, REQUEST_DELAY, MAX_RETRIES,
)


class WBApi:
    """Клиент для публичного API Wildberries."""

    def __init__(self, dest: int = DEFAULT_DEST, proxy: Optional[str] = None):
        self.dest = dest
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self._last_request_time = 0

    def _throttle(self):
        """Задержка между запросами для избежания бана."""
        elapsed = time.time() - self._last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self._last_request_time = time.time()

    def _get(self, url: str, params: dict = None) -> Optional[dict]:
        """GET-запрос с ретраями."""
        self._throttle()
        for attempt in range(MAX_RETRIES):
            try:
                resp = self.session.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 429:
                    wait = 2 ** (attempt + 1)
                    print(f"[!] Rate limit, жду {wait}с...")
                    time.sleep(wait)
                    continue
                if resp.status_code in (403, 503):
                    print(f"[!] Блокировка ({resp.status_code}), попытка {attempt + 1}/{MAX_RETRIES}")
                    time.sleep(2 ** (attempt + 1))
                    continue
                print(f"[!] HTTP {resp.status_code} для {url}")
                return None
            except requests.RequestException as e:
                print(f"[!] Ошибка запроса: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** (attempt + 1))
        return None

    def search(self, query: str, page: int = 1, sort: str = "popular") -> Optional[dict]:
        """Поиск товаров по запросу.

        sort: popular, priceup, pricedown, rate, newly
        """
        params = {
            "appType": 1,
            "curr": DEFAULT_CURRENCY,
            "dest": self.dest,
            "lang": "ru",
            "locale": "ru",
            "page": page,
            "query": query,
            "resultset": "catalog",
            "sort": sort,
            "spp": DEFAULT_SPP,
            "suppressSpellcheck": "false",
        }
        return self._get(SEARCH_URL, params)

    def get_product_detail(self, product_ids: list[int]) -> Optional[dict]:
        """Получить детальную информацию по товарам (до 100 за раз)."""
        nm = ";".join(str(pid) for pid in product_ids[:100])
        params = {
            "appType": 1,
            "curr": DEFAULT_CURRENCY,
            "dest": self.dest,
            "spp": DEFAULT_SPP,
            "nm": nm,
        }
        return self._get(CARD_DETAIL_URL, params)

    def get_feedbacks(self, product_id: int, page: int = 1) -> Optional[dict]:
        """Получить отзывы на товар."""
        # WB распределяет отзывы по серверам 1-2
        for num in range(1, 3):
            url = FEEDBACKS_URL.format(num=num, product_id=product_id)
            params = {
                "imtId": product_id,
                "skip": (page - 1) * 30,
                "take": 30,
                "order": "dateDesc",
            }
            result = self._get(url, params)
            if result and result.get("feedbacks"):
                return result
        return None

    def get_sales_count(self, product_ids: list[int]) -> Optional[dict]:
        """Получить количество продаж."""
        params = [("nm", pid) for pid in product_ids]
        return self._get(SALES_URL, params)

    def get_catalog_menu(self) -> Optional[list]:
        """Получить дерево категорий."""
        result = self._get(CATALOG_MENU_URL)
        return result if isinstance(result, list) else None
