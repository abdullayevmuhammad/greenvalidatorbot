import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # ✅ .env faylidan haqiqiy tokenni oladi
API_BASE_URL = "http://127.0.0.1:8000/api/applicants/"
