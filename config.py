"""
Konfiguratsiya fayli.
Barcha maxfiy va sozlanuvchi qiymatlar shu yerda saqlanadi.
Production'da BOT_TOKEN ni Railway "Variables" bo'limida environment
o'zgaruvchisi sifatida saqlash tavsiya etiladi (xavfsizlik uchun).
"""

import os

# --- Bot tokeni ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8910822725:AAHiUq4cZnX6BACEHlLgSKFcL8lDMvIJs_A")

# --- Admin ---
ADMIN_ID = int(os.getenv("ADMIN_ID", "8914193938"))

# --- Majburiy obuna kanallari ---
REQUIRED_CHANNELS = [
    {"name": "Free Fire Panel Chat", "username": "freefirepanelchit"},
    {"name": "Free Fire Chat UZ", "username": "FREEFIRECHAT_UZBEKI"},
    {"name": "Free Fire O'zbekiston", "username": "FREE_FIRE_OZBEKISTON_17"},
    {"name": "FF Panel Chat", "username": "ffpanelchit"},
    {"name": "Xon Fire Stream", "username": "xonfirestream"},
]

# /yangiliklar bosilganda avtomatik yo'naltiriladigan kanal
NEWS_CHANNEL_URL = "https://t.me/FREE_FIRE_OZBEKISTON_17"

# Yordam uchun murojaat manzili
HELP_CONTACT = "@ffhelpnastroyka"

# Premium bo'lim uchun aloqa
PREMIUM_CONTACT = "@auwsn"

# --- Ma'lumotlar bazasi ---
DB_PATH = os.getenv("DB_PATH", "database.db")

# --- Free Fire ID tekshirish API ---
# free-ff-api (community, bepul, kalitsiz) xizmatidan foydalanadi.
FF_API_URL = os.getenv("FF_API_URL", "https://free-ff-api-src-5plp.onrender.com/api/v1/account")
FF_REGION = os.getenv("FF_REGION", "CIS")

BOT_NAME = "🎮 O'yin Sirlari"
