DOMAIN = "marktguru"
CONFIG_VERSION = 2

CONF_ZIP_CODE = "zip_code"
CONF_CLIENT_KEY = "client_key"
CONF_API_KEY = "api_key"
CONF_PRODUCTS = "products"
CONF_ALLOWED_RETAILERS = "allowed_retailers"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 12

DEFAULT_ALLOWED_RETAILERS = [
    "REWE",
    "Kaufland",
    "Netto Marken-Discount",
    "EDEKA",
    "V-Markt",
]

KNOWN_RETAILERS = [
    "ALDI Nord",
    "ALDI Süd",
    "EDEKA",
    "Kaufland",
    "Lidl",
    "Netto Marken-Discount",
    "Penny",
    "REWE",
    "V-Markt",
    "dm",
    "Rossmann",
    "Globus",
    "K+K",
    "Markkauf",
    "Teegut",
    "Famila",
    "E-Center",
    "Comet",
    "Budni",
    "Plaza",
]

API_URL = "https://api.marktguru.de/api/v1/offers/search"

# Public keys embedded in the Marktguru web app; shared publicly by the
# community (see thorschtn/ha-marktguru). They are not secrets.
DEFAULT_CLIENT_KEY = "WU/RH+PMGDi+gkZer3WbMelt6zcYHSTytNB7VpTia90="
DEFAULT_API_KEY = "8Kk+pmbf7TgJ9nVj2cXeA7P5zBGv8iuutVVMRfOfvNE="

EXCLUDE_KEYWORDS = ["online", "app-coupon"]

API_LIMIT = 24
