"""Конфигурация парсера госзакупок."""

# API госзакупок
ZAKUPKI_API_URL = "https://zakupki.gov.ru/api/v1"
ZAKUPKI_SEARCH_URL = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html"

# Заголовки
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

# Лимиты
REQUEST_DELAY = 2.0  # Задержка между запросами (сек)
MAX_RETRIES = 3
RESULTS_PER_PAGE = 50

# Фильтры по умолчанию
DEFAULT_FILTERS = {
    "fz": "44",           # 44-ФЗ
    "af": "on",           # Аукцион
    "ca": "on",           # Конкурс
    "pc": "on",           # Запрос котировок
}

# Категории для мониторинга (ОКПД2 коды)
MONITORED_CATEGORIES = {
    "it_services": "62",           # Разработка ПО и консультирование
    "construction": "41",          # Строительство зданий
    "cleaning": "81.2",            # Услуги по уборке
    "security": "80.1",            # Охранная деятельность
    "food_supply": "10",           # Производство пищевых продуктов
    "office_supplies": "17.12",    # Бумага и картон
}

# Экспорт
OUTPUT_DIR = "output"
