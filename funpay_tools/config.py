"""Конфигурация FunPay Tools."""

# FunPay
FUNPAY_BASE_URL = "https://funpay.com"
FUNPAY_LOTS_URL = "https://funpay.com/lots"

# Заголовки
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

# Лимиты
REQUEST_DELAY = 1.0  # Задержка между запросами (сек)
MAX_RETRIES = 3

# Популярные категории SMM на FunPay (ID лотов)
SMM_CATEGORIES = {
    "telegram_subscribers": "/lots/offer/telegram-subscribers",
    "instagram_followers": "/lots/offer/instagram-followers",
    "tiktok_followers": "/lots/offer/tiktok-followers",
    "youtube_subscribers": "/lots/offer/youtube-subscribers",
    "vk_followers": "/lots/offer/vk-friends",
}

# Популярные SMM-панели (оптовые)
SMM_PANELS = [
    {"name": "SMMStone", "url": "https://smmstone.com", "description": "Популярная RU панель"},
    {"name": "Market-SMM", "url": "https://market-smm.pro", "description": "Бюджетная панель"},
    {"name": "JustAnotherPanel", "url": "https://justanotherpanel.com", "description": "Международная панель"},
]

# Экспорт
OUTPUT_DIR = "output"
