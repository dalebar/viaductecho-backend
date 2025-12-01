import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL")

    # OpenAI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # GitHub configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

    # API configuration
    API_TITLE = os.getenv("API_TITLE", "Viaduct Echo API")
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    API_DESCRIPTION = os.getenv(
        "API_DESCRIPTION", "REST API for the Viaduct Echo news aggregation system"
    )

    # CORS configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # Pagination defaults
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))

    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

    # HTTP client defaults
    # Use None to preserve previous no-timeout behavior unless explicitly configured
    _timeout = os.getenv("HTTP_TIMEOUT", "").strip()
    HTTP_TIMEOUT = float(_timeout) if _timeout else None

    KEYWORDS = [
        "stockport",
        "manchester",
        "macclesfield",
        "wilmslow",
        "altrincham",
        "sale",
        "urmston",
        "stretford",
        "chorlton",
        "didsbury",
        "burnage",
        "levenshulme",
        "longsight",
        "fallowfield",
        "withington",
        "wythenshawe",
        "oldham",
        "rochdale",
        "bury",
        "bolton",
        "salford",
        "eccles",
        "swinton",
        "worsley",
        "walkden",
        "farnworth",
        "little lever",
        "kearsley",
        "prestwich",
        "whitefield",
        "radcliffe",
        "ramsbottom",
        "tottington",
        "heywood",
        "middleton",
        "chadderton",
        "shaw",
        "royton",
        "lees",
        "mossley",
        "stalybridge",
        "hyde",
        "denton",
        "audenshaw",
        "dukinfield",
        "ashton-under-lyne",
        "droylsden",
        "failsworth",
        "moston",
        "blackley",
        "crumpsall",
        "cheetham hill",
        "higher blackley",
        "harpurhey",
        "collyhurst",
        "newton heath",
        "clayton",
        "openshaw",
        "gorton",
        "belle vue",
        "reddish",
        "bredbury",
        "marple",
        "poynton",
        "bollington",
        "knutsford",
        "northwich",
        "winsford",
        "middlewich",
        "sandbach",
        "crewe",
        "nantwich",
        "congleton",
        "buxton",
        "glossop",
        "hadfield",
        "new mills",
        "whaley bridge",
        "chapel-en-le-frith",
        "high peak",
    ]

    # Skiddle API configuration
    SKIDDLE_API_KEY = os.getenv("SKIDDLE_API_KEY")

    # Events geo configuration (Stockport town centre)
    EVENTS_LATITUDE = float(os.getenv("EVENTS_LATITUDE", "53.4106"))
    EVENTS_LONGITUDE = float(os.getenv("EVENTS_LONGITUDE", "-2.1575"))
    EVENTS_RADIUS_MILES = int(os.getenv("EVENTS_RADIUS_MILES", "10"))

    # Events fetch settings
    EVENTS_FETCH_DAYS_AHEAD = int(os.getenv("EVENTS_FETCH_DAYS_AHEAD", "60"))

    # Valid SK postcodes prefix for filtering
    VALID_POSTCODE_PREFIXES = ["SK"]

    # Event type mappings from Skiddle codes
    SKIDDLE_EVENT_TYPE_MAP = {
        "LIVE": "music",
        "CLUB": "music",
        "FEST": "music",
        "COMEDY": "comedy",
        "THEATRE": "theatre",
        "EXHIB": "arts",
        "KIDS": "family",
        "BARPUB": "community",
        "DATE": "other",
    }

    # Admin API configuration
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "viaduct-echo-admin-2025")
