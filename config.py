"""
Konfiguratsiya fayli.
Barcha maxfiy va sozlanuvchi qiymatlar shu yerda saqlanadi.
Production'da BOT_TOKEN ni Railway "Variables" bo'limida environment
o'zgaruvchisi sifatida saqlash tavsiya etiladi (xavfsizlik uchun).
"""

import os

# --- Bot tokeni ---
# Railway'da Variables bo'limiga BOT_TOKEN nomi bilan qo'shish tavsiya etiladi.
# Agar environment o'zgaruvchisi topilmasa, quyidagi standart token ishlatiladi.
BOT_TOKEN = os.getenv("BOT_TOKEN", "8910822725:AAHiUq4cZnX6BACEHlLgSKFcL8lDMvIJs_A")

# --- Admin ---
ADMIN_ID = int(os.getenv("ADMIN_ID", "8914193938"))

# --- Majburiy obuna kanallari ---
# username formatida (bot shu kanallarda ADMIN bo'lishi shart, aks holda
# obuna tekshiruvi ishlamaydi)
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

# --- Free Fire ID tekshirish API (ixtiyoriy) ---
# Bu yerga haqiqiy Free Fire ID API manzili va tokenini qo'shishingiz mumkin.
# Masalan: https://rapidapi.com dagi "Free Fire" nomli xizmatlardan biri.
# API topilmagan/sozlanmagan bo'lsa, bot foydalanuvchiga tegishli xabar beradi.
FF_API_URL = os.getenv("FF_API_URL", "")
FF_API_KEY = os.getenv("FF_API_KEY", "")

BOT_NAME = "🎮 O'yin Sirlari"
