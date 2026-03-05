"""Configuration for EU TED (Tenders Electronic Daily) Parser."""

# TED API (public procurement above EU thresholds)
TED_API_URL = "https://api.ted.europa.eu/v3"
TED_SEARCH_URL = f"{TED_API_URL}/notices/search"

HEADERS = {
    "User-Agent": "DataMiner/1.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

REQUEST_DELAY = 1.0
MAX_RETRIES = 3
RESULTS_PER_PAGE = 100

# CPV codes (Common Procurement Vocabulary) — major categories
CPV_CATEGORIES = {
    "it_services": "72000000",       # IT services
    "software_dev": "72200000",      # Software development
    "consulting": "79400000",        # Management consulting
    "construction": "45000000",      # Construction work
    "cleaning": "90910000",          # Cleaning services
    "security": "79710000",          # Security services
    "transport": "60000000",         # Transport services
    "medical": "33000000",           # Medical equipment
    "food": "15000000",              # Food products
    "office_supplies": "30190000",   # Office equipment
    "training": "80500000",          # Training services
    "research": "73000000",          # R&D services
}

# Country codes
EU_COUNTRIES = {
    "DE": "Germany", "FR": "France", "IT": "Italy", "ES": "Spain",
    "NL": "Netherlands", "BE": "Belgium", "AT": "Austria", "PL": "Poland",
    "SE": "Sweden", "DK": "Denmark", "FI": "Finland", "IE": "Ireland",
    "PT": "Portugal", "CZ": "Czech Republic", "RO": "Romania",
    "GR": "Greece", "HU": "Hungary", "BG": "Bulgaria", "SK": "Slovakia",
    "HR": "Croatia", "LT": "Lithuania", "SI": "Slovenia", "LV": "Latvia",
    "EE": "Estonia", "CY": "Cyprus", "LU": "Luxembourg", "MT": "Malta",
    # EEA
    "NO": "Norway", "IS": "Iceland", "LI": "Liechtenstein",
    # Recently left but still relevant
    "GB": "United Kingdom",
}

OUTPUT_DIR = "output"
