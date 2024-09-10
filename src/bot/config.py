from os import getenv


BOT_TOKEN = getenv("BOT_TOKEN")

FAQ_LINK = getenv("FAQ_LINK") or "https://t.me"
SUPPORT_BOT_LINK = getenv("SUPPORT_BOT_LINK") or "https://t.me"

API_SERVICE_NAME = getenv("API_SERVICE_NAME")
API_SERVICE_PORT = getenv("API_SERVICE_PORT")
