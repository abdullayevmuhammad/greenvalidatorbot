import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# ---- API bazasi ----
# Masalan:
#   API_BASE_URL=http://127.0.0.1:8000
#   API_PREFIX=/trash               (bo'sh ham bo'lishi mumkin)
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_PREFIX   = (os.getenv("API_PREFIX", "/api") or "").strip("/")
BASE_URL = "http://127.0.0.1:8000/api"
# /trash prefiksi bo'lsa ulaymiz
API_ROOT = f"{API_BASE_URL}/{API_PREFIX}" if API_PREFIX else API_BASE_URL

# Auth (agar DRF Token/JWT ishlatsangiz)
API_TOKEN = os.getenv("API_TOKEN", "").strip()

# Asosiy resurslar
API_APPLICANTS_URL = f"{API_ROOT}/applicants/" # trailing-slash qo‘ymaymiz
# DRF default: endpointlar trailing slash bilan tugaydi → so'rovda "/"" qo‘shib yuboramiz
