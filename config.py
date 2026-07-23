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

# --- Admin bilan to'g'ridan-to'g'ri bog'lanish uchun username ---
# E'TIBOR: shu yerga o'zingizning haqiqiy Telegram username'ingizni yozing
# (masalan "auwsn"), aks holda "Admin orqali olish" tugmasi ishlamaydi.
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "auwsn")

# --- To'lov kartasi ma'lumotlari (Hisobim -> Humo/Uzcard orqali to'ldirish) ---
CARD_NUMBER = os.getenv("CARD_NUMBER", "9860 0366 3090 0060")
CARD_HOLDER_NAME = os.getenv("CARD_HOLDER_NAME", "Bilolxonova Tursunoy")
CARD_PHONE = os.getenv("CARD_PHONE", "+998 94 595 92 06")

# --- Ma'lumotlar bazasi ---
DB_PATH = os.getenv("DB_PATH", "database.db")

# --- Free Fire ID tekshirish API ---
# free-ff-api (community, bepul, kalitsiz) xizmatidan foydalanadi.
FF_API_URL = os.getenv("FF_API_URL", "https://free-ff-api-src-5plp.onrender.com/api/v1/account")
FF_REGION = os.getenv("FF_REGION", "CIS")

# --- "Foydali web sayt" tugmasi ochadigan havola ---
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://freefireuz.netlify.app")

BOT_NAME = "🎮 O'yin Sirlari"
