"""Конфигурация парсера Wildberries."""

# Базовые URL (WB мигрирует на wildberries.ru, поддерживаем оба)
SEARCH_URL = "https://search.wb.ru/exactmatch/ru/common/v7/search"
CARD_DETAIL_URL = "https://card.wb.ru/cards/v2/detail"
CATALOG_MENU_URL = "https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json"
FEEDBACKS_URL = "https://feedbacks{num}.wb.ru/feedbacks/v2/{product_id}"
SALES_URL = "https://product-order-qnt.wildberries.ru/by-nm/"

# Дефолтные параметры запросов
DEFAULT_DEST = -1257786  # Москва
DEFAULT_CURRENCY = "rub"
DEFAULT_SPP = 30  # Процент скидки продавца

# Заголовки для имитации браузера
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.wildberries.ru",
    "Referer": "https://www.wildberries.ru/",
}

# Лимиты
REQUEST_DELAY = 0.3  # Задержка между запросами (сек)
MAX_PAGES = 50  # Макс. страниц при поиске
PRODUCTS_PER_PAGE = 100  # Товаров на странице
MAX_RETRIES = 3  # Повторных попыток при ошибке

# Экспорт
DEFAULT_OUTPUT_DIR = "output"
