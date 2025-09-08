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
