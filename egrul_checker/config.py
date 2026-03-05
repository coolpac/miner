"""Конфигурация ЕГРЮЛ Checker."""

# API ФНС
FNS_EGRUL_URL = "https://egrul.nalog.ru/"
FNS_SEARCH_URL = "https://egrul.nalog.ru/index.html"
FNS_API_SEARCH = "https://egrul.nalog.ru/"

# ФССП (судебные приставы)
FSSP_API_URL = "https://api-ip.fssprus.ru/api/v1.0"
FSSP_TOKEN = ""  # Получить на https://api-ip.fssprus.ru/

# Заголовки
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

# Лимиты
REQUEST_DELAY = 1.5
MAX_RETRIES = 3

# Экспорт
OUTPUT_DIR = "output"
