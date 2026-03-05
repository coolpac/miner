"""Configuration for US Building Permit Scraper."""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_DELAY = 1.5  # seconds between requests
MAX_RETRIES = 3

# Open data portals for building permits (Socrata-based and others)
# Format: {city: {url, dataset_id, api_type}}
PERMIT_SOURCES = {
    "new_york_city": {
        "name": "New York City",
        "state": "NY",
        "api_type": "socrata",
        "domain": "data.cityofnewyork.us",
        "dataset_id": "ipu4-2vj7",  # DOB Permit Issuance
        "description": "NYC DOB permit issuance data",
    },
    "los_angeles": {
        "name": "Los Angeles",
        "state": "CA",
        "api_type": "socrata",
        "domain": "data.lacity.org",
        "dataset_id": "yv23-pmwf",  # Building Permits
        "description": "LA building & safety permits",
    },
    "chicago": {
        "name": "Chicago",
        "state": "IL",
        "api_type": "socrata",
        "domain": "data.cityofchicago.org",
        "dataset_id": "ydr8-5enu",  # Building Permits
        "description": "Chicago building permits",
    },
    "houston": {
        "name": "Houston",
        "state": "TX",
        "api_type": "socrata",
        "domain": "data.houstontx.gov",
        "dataset_id": "pa6f-gxda",  # Construction Permits
        "description": "Houston construction permits issued",
    },
    "san_francisco": {
        "name": "San Francisco",
        "state": "CA",
        "api_type": "socrata",
        "domain": "data.sfgov.org",
        "dataset_id": "i98e-djp9",  # Building Permits
        "description": "SF building permits",
    },
    "seattle": {
        "name": "Seattle",
        "state": "WA",
        "api_type": "socrata",
        "domain": "data.seattle.gov",
        "dataset_id": "76t5-zuj6",  # Building Permits
        "description": "Seattle building permits",
    },
    "austin": {
        "name": "Austin",
        "state": "TX",
        "api_type": "socrata",
        "domain": "data.austintexas.gov",
        "dataset_id": "3syk-w9eu",  # Issued Construction Permits
        "description": "Austin issued construction permits",
    },
    "denver": {
        "name": "Denver",
        "state": "CO",
        "api_type": "socrata",
        "domain": "data.denvergov.org",
        "dataset_id": "p2g4-fmyh",  # Building Permits
        "description": "Denver building permits",
    },
    "portland": {
        "name": "Portland",
        "state": "OR",
        "api_type": "socrata",
        "domain": "data.portland.gov",
        "dataset_id": "fmre-feels",
        "description": "Portland building permits",
    },
    "philadelphia": {
        "name": "Philadelphia",
        "state": "PA",
        "api_type": "socrata",
        "domain": "phl.carto.com",
        "dataset_id": "permits",
        "description": "Philadelphia L+I permits",
    },
}

# Permit types to track (normalized)
PERMIT_TYPES = {
    "new_building": ["NB", "NEW", "NEW BUILDING", "New Construction"],
    "alteration": ["ALT", "ALTERATION", "ALT1", "ALT2", "Alteration"],
    "demolition": ["DM", "DEMO", "DEMOLITION", "Demolition"],
    "electrical": ["EL", "ELEC", "ELECTRICAL", "Electrical"],
    "plumbing": ["PL", "PLMB", "PLUMBING", "Plumbing"],
    "mechanical": ["ME", "MECH", "MECHANICAL", "HVAC", "Mechanical"],
    "solar": ["SOLAR", "PV", "PHOTOVOLTAIC", "Solar"],
    "roofing": ["ROOF", "ROOFING", "Roofing"],
}

OUTPUT_DIR = "output"
