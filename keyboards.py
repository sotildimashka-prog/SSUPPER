# -*- coding: utf-8 -*-
"""Reply va Inline klaviaturalarni yaratish."""

from urllib.parse import quote

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

import database as db
from config import (
    REQUIRED_CHANNELS,
    ADMIN_ID,
    WEBSITE_URL,
    WEBAPP_URL,
    NEWS_CHANNEL_URL,
    ORDERS_CHANNEL_ID,
    ADMIN_USERNAME,
)
from data.settings_data import PHONES
from data.tablet_data import TABLETS
from data.pc_data import PC_MODELS
from data.guides_data import GUIDES
from data.diamonds_data import PACKAGES, SUBSCRIPTIONS, button_label


import re
import inspect
import functools

from data.premium_emoji_ids import EMOJI_IDS

_EMOJI_PREFIX_RE = re.compile(
    r"^([\U0001F000-\U0001FFFF\u2600-\u27BF\u2B00-\u2BFF]\uFE0F?)\s*"
)


def _apply_emoji_icon(text: str, kwargs: dict) -> str:
    """Faqat INLINE tugmalar uchun: agar matn boshida emoji bo'lsa va unga ID
    mavjud bo'lsa, icon_custom_emoji_id qo'shadi va matndan native emojini
    olib tashlaydi (takrorlanmasligi uchun)."""
    if "icon_custom_emoji_id" in kwargs:
        return text
    match = _EMOJI_PREFIX_RE.match(text)
    if match:
        emoji = match.group(1)
        emoji_id = EMOJI_IDS.get(emoji, "")
        if emoji_id:
            kwargs["icon_custom_emoji_id"] = emoji_id
            return text[match.end():].strip()
    return text


# Inline tugmalar: standart holatda RANGSIZ (oddiy, style berilmaydi).
def _ikb(text, style=None, **kwargs):
    display_text = _apply_emoji_icon(text, kwargs)
    if style:
        kwargs["style"] = style
    try:
        return InlineKeyboardButton(display_text, **kwargs)
    except TypeError:
        # Eski python-telegram-bot versiyasida 'style' parametri qo'llab-
        # quvvatlanmasligi mumkin - shunday holatda uni olib tashlab qayta
        # urinamiz (butun klaviatura qulab tushmasligi uchun).
        kwargs.pop("style", None)
        return InlineKeyboardButton(display_text, **kwargs)


# Pastki (Reply) klaviatura tugmalari: standart holatda RANGSIZ (oddiy).
def _kb(text, style=None, **kwargs):
    # MUHIM: ReplyKeyboard tugmasi bosilganda uning YANGI (icon qo'shilgandan
    # keyingi) matni xabar sifatida botga yuboriladi. Agar emojiga
    # custom_emoji_id topilsa, matn boshidagi native emoji olib tashlanadi
    # (icon uni almashtiradi) - shuning uchun bot.py dagi _exact() filtri
    # ham emoji bor/yo'qligidan qat'i nazar mos kelishi uchun moslashtirilgan.
    display_text = _apply_emoji_icon(text, kwargs)
    try:
        return KeyboardButton(display_text, style=style, **kwargs)
    except TypeError:
        # Eski python-telegram-bot versiyasida 'style' parametri qo'llab-
        # quvvatlanmasligi mumkin - shunday holatda ranglashtirmasdan oddiy
        # tugma qaytaramiz (butun menyu qulab tushib, hech narsa
        # ko'rinmasligining oldini olish uchun MUHIM fallback).
        kwargs.pop("icon_custom_emoji_id", None)
        return KeyboardButton(text, **kwargs)

# ============================================================================
# 🆘 Har bir INLINE menyuning tagiga avtomatik qo'shiladigan qatorlar:
#   1) Agar menyuda hech qanday "orqaga/bosh menyu" tugmasi bo'lmasa -
#      "🎮 Free Fire menyu" tugmasi (bosh menyuga qaytaradi).
#   2) Har doim, eng pastda - QIZIL rangdagi "🎧 Yordam" tugmasi. Bu tugma
#      callback emas, balki to'g'ridan-to'g'ri admin (@auwsn) bilan
#      shaxsiy chatga o'tkazadigan URL tugmasi.
# ============================================================================

GOTOMAINMENU_CB = "gotomainmenu"
HELP_ADMIN_URL = f"https://t.me/{ADMIN_USERNAME}"

_NAV_HINT_WORDS = (
    "orqaga",
    "ortga",
    "menyu",
    "yopish",
    "bekor",
    "ro'yxat",
    "royxat",
    "qaytish",
    "qaytar",
)


def _looks_like_nav_button(text: str, callback_data) -> bool:
    lowered = (text or "").lower()
    if any(word in lowered for word in _NAV_HINT_WORDS):
        return True
    if isinstance(callback_data, str):
        cb = callback_data.lower()
        if cb.endswith(":back") or "back" in cb or cb == GOTOMAINMENU_CB:
            return True
    return False


def _has_nav_button(rows) -> bool:
    for row in rows:
        for btn in row:
            if _looks_like_nav_button(getattr(btn, "text", ""), getattr(btn, "callback_data", None)):
                return True
    return False


def _with_ff_menu_and_help(markup, skip_nav: bool = False):
    """Har qanday InlineKeyboardMarkup obyektini qabul qilib, tagiga
    kerak bo'lsa "🎮 Free Fire menyu" va har doim qizil "🎧 Yordam"
    tugmalarini qo'shib qaytaradi. Boshqa turdagi qiymatlar (masalan
    ReplyKeyboardMarkup yoki None) o'zgarishsiz qaytariladi.

    skip_nav=True bo'lsa, "🎮 Free Fire menyu" tugmasi HECH QACHON
    qo'shilmaydi (masalan, bu klaviaturaning o'zi allaqachon bosh
    menyu bo'lsa - start_inline_keyboard())."""
    if not isinstance(markup, InlineKeyboardMarkup):
        return markup

    rows = [list(row) for row in markup.inline_keyboard]

    if not skip_nav and not _has_nav_button(rows):
        rows.append(
            [_ikb("🎮 Free Fire menyu", style="success", callback_data=GOTOMAINMENU_CB)]
        )

    rows.append(
        [_ikb("🔐 Yordam", style="danger", url=HELP_ADMIN_URL)]
    )

    return InlineKeyboardMarkup(rows)


# ---------- Asosiy menyu (ReplyKeyboard) ----------

BTN_SETTINGS = "⚙️ Telefon nastroyka"
BTN_TABLET = "⚙️ Planshet nastroyka"
BTN_NICKS = "🎮 Free Fire niklar"
BTN_HACK = "⚠️ Maxsus xizmat"
BTN_CUSTOM = "⚠️ Shaxsiy nastroyka"
BTN_WEBSITE = "🏆 Free Fire Turnirlar"
BTN_NEWS = "📰 Free Fire yangiliklari"
BTN_MUSIC = "🎵 Free Fire qo'shiq"
BTN_QUIZ = "💎 Tekin almaz"
BTN_DIAMONDS = "💎 Almaz xarid qilish"
BTN_ACCOUNT = "💰 Mening hisobim"
BTN_HELP = "🎧 Yordam"
BTN_GUIDES = "📚 Qo'llanmalar"
BTN_FAQ = "📬 Savollar (FAQ)"
BTN_STATS = "📈 Statistika"
BTN_BROADCAST = "📣 Xabar yuborish"
BTN_POST = "🖋️ Post"
BTN_EDIT_TEXTS = "✏️ Tugmalarni tahrirlash"


BTN_WITHDRAW = "💎 Almaz yechish"

BTN_ADMIN_CREDIT = "🛠 Admin buyrug'i"
BTN_GIFT_ALL = "🎁 Hammaga sovg'a"
BTN_DEDUCT_DIAMOND = "➖ Almazni ayirish"
BTN_DEDUCT_ALL_DIAMONDS = "🗑 Hammadan almaz yechish"
BTN_FF_ADMIN_PANEL = "🗂 Turnir/Akkaunt boshqaruvi"

# ---------- 🛒 Free Fire Do'koni / 🎁 Giftlar / 🏆 Yutiqni chiqarish ----------
BTN_STORE = "🛒 Free Fire Do'koni"
BTN_GIFT_ORDER = "🎁 Giftlar"
BTN_WITHDRAW_WIN = "🏆 Yutiqni chiqarish"

# ---------- Yangi Bosh menyu (faqat 4 ta tugma) ----------

BTN_MAIN_FF = "🎮 Free Fire"
BTN_MAIN_DIAMONDS = "💎 Almaz olish"
BTN_MAIN_SERVICES = "🛠️ Xizmatlar"
BTN_MAIN_PROFILE = "👤 Profil"

# ---------- 🆕 Asosiy menyu (6 ta tugma, 2 ustunda) ----------
# 💎 Almaz olish     | 🛍 Xizmatlar
# ⚙️ Nastroykalar    | 🎉 Free Fire Niklar
# 💰 To'lov usullari | 📬 Savollar (FAQ)

BTN_M2_DIAMONDS = "💎 Almaz olish"
BTN_M2_SERVICES = "🛍 Xizmatlar"
BTN_M2_SETTINGS = "⚙️ Nastroykalar"
BTN_M2_NICKS = "🎉 Free Fire Niklar"
BTN_M2_PAYMENTS = "💰 To'lov usullari"
BTN_M2_FAQ = "📬 Savollar (FAQ)"
BTN_GIFTS = "🎁 Sovg'alar"
BTN_PORTAL = "🗺 Free Fire Portal 🚀"
BTN_MINI_GAMES = "🎮 Mini O'yinlar"
BTN_MY_ACCOUNT = "👛 Balansim"

# ---------- 🖼️ Rasm Yasash / 🎬 Video Yasash (Bosh menyu) ----------

BTN_MAIN_RASM = "🖼️ Rasm Yasash"
BTN_MAIN_VIDEO = "🎬 Video Yasash"
BTN_MAIN_MUSIC = "🎵 Musiqa yaratish"

# ---------- 👑 Pro obuna ----------

BTN_PRO_SUB = "👑 Pro obuna"

# ---------- 📢 Buyurtmalar kanali ----------

BTN_ORDERS_CHANNEL = "📢 Buyurtmalar"

# ---------- 🔙 Universal "Orqaga" (Reply) tugmasi ----------
# Ichki bo'limlarning istalgan tugmasi bosilganda pastda shu tugma chiqib,
# foydalanuvchi asosiy menyuga bir bosishda qaytishi mumkin.

BTN_BACK = "🔙 Orqaga"


def back_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[_kb(BTN_BACK)]], resize_keyboard=True, is_persistent=True
    )


# ---------- 🛠 Admin paneli (faqat ADMIN_ID uchun ko'rinadigan pastki menyu) ----------
# Eslatma: bosh menyu endi hamma uchun (admin uchun ham) inline tugmalarga
# o'tkazilgan (main_menu_keyboard() endi ReplyKeyboardRemove() qaytaradi),
# shu sabab quyidagi tugmalar (Statistika, Nastroyka qo'shish, Turnir
# boshqaruvi va h.k.) hech qayerda ko'rinmay qolgan edi - handler'lari
# hali ham ishlaydi, lekin ularni bosish uchun panel kerak edi. Shu panel
# /admin buyrug'i orqali ochiladi (faqat ADMIN_ID uchun).
def admin_panel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [_kb(BTN_STATS), _kb(BTN_ADMIN_CREDIT)],
            [_kb(BTN_BROADCAST), _kb(BTN_GIFT_ALL)],
            [_kb(BTN_POST), _kb(BTN_EDIT_TEXTS)],
            [_kb(BTN_NASTROYKA_ADD), _kb(BTN_FF_ADMIN_PANEL)],
            [_kb(BTN_DEDUCT_DIAMOND), _kb(BTN_DEDUCT_ALL_DIAMONDS)],
            [_kb(BTN_BACK)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


VIDEO_MIN_BALANCE = 30000

ORDERS_CHANNEL_USERNAME = ORDERS_CHANNEL_ID.lstrip("@")

# Har safar pastki (Reply) tugmalar tarkibi yoki rangi o'zgarganda bu
# raqamni +1 oshiring. Shunda barcha foydalanuvchilarning eski (keshlangan)
# tugmalar oynasi ular botga keyingi safar yozganda YOKI istalgan tugmani
# (reply yoki inline) bosganda AVTOMATIK yangilanadi — broadcast yuborish
# shart emas.
MENU_VERSION = 10


def full_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """MUHIM (foydalanuvchi so'rovi bo'yicha): ESKI, katta pastki
    (Reply) menyu (🛒 Do'kon, 🎁 Giftlar, 👑 Pro obuna, 🏆 Yutiqni
    chiqarish va h.k. - o'nlab tugma) ENDI BOTNING HECH BIR JOYIDA
    ko'RSATILMAYDI. Butun botda endi FAQAT yangi menyu (inline: ⚙️
    Nastroykalar / ✨ Nik yaratish / 📰 News / 👤 Hisobim -
    start_inline_keyboard()) va har bir bo'lim tagidagi qizil
    "🔐 Yordam" tugmasi ishlatiladi.

    Funksiya butunlay o'chirilmagan (faqat bo'sh natija qaytaradi) -
    shunchaki uni chaqiradigan o'nlab joy (handlers/*.py) buzilib
    qolmasligi uchun. Mavjud bo'lsa, foydalanuvchidagi eski pastki
    tugmalar oynasini ham olib tashlaydi (ReplyKeyboardRemove)."""
    return ReplyKeyboardRemove()


# ---------- 🆕 /start xabari (rasm + 3 ta inline tugma) ----------

NEWS_CHANNEL_USERNAME = "xonfirestream"

START_ACCOUNT_CB = "start:account"
START_SERVICES_CB = "start:services"


NIMAGAP_CB = "nimagap:menu"


HSPRO_INTRO_CB = "hspro:start"
ALMAZ_ISHLASH_CB = "almazish:start"
ALMAZ_PAGE1_CB = "almazish:1"
ALMAZ_PAGE2_CB = "almazish:2"
ALMAZ_GO_CB = "almazish:go"
ALMAZ_ACCOUNT_CB = "almazish:account"


# ---------- 🏆 Top foydalanuvchilar reytingi ----------

TOP_USERS_CB = "topusers:show"
TOP_USERS_REF_CB = "topusers:ref"
TOP_USERS_DIAMOND_CB = "topusers:dia"


def top_users_keyboard(active: str = "ref") -> InlineKeyboardMarkup:
    """active: 'ref' (referallar) yoki 'dia' (almazlar) - hozir qaysi
    bo'lim ko'rsatilayotganini belgilaydi (u tugma bosilmaydigan holatda
    ko'rsatiladi).

    MUHIM: pastdagi "🔙 Orqaga" tugmasi ataylab "start:back" ga
    ulangan - shu orqali foydalanuvchi haqiqiy asosiy menyuga (📰 News,
    ⚙️ Nastroykalar, ✨ Nik yaratish, 👤 Hisobim va h.k. tugmalari bilan)
    qaytadi. Bundan tashqari, shu matn ("orqaga") tufayli
    _with_ff_menu_and_help() bu yerga "🎮 Free Fire menyu" tugmasini
    endi QO'SHMAYDI (chunki nav tugmasi allaqachon mavjud deb topadi)."""
    ref_label = "✅ 👥 Referallar" if active == "ref" else "👥 Referallar"
    dia_label = "✅ 💎 Almazlar" if active == "dia" else "💎 Almazlar"
    return InlineKeyboardMarkup(
        [
            [
                _ikb(ref_label, callback_data=TOP_USERS_REF_CB),
                _ikb(dia_label, callback_data=TOP_USERS_DIAMOND_CB),
            ],
            [_ikb("🔙 Orqaga", callback_data="start:back")],
        ]
    )


def start_inline_keyboard() -> InlineKeyboardMarkup:
    """/start bosilganda chiqadigan inline tugmalar: ⚙️ Nastroykalar,
    ✨ Nik yaratish, 🎮 Nima gap?, 👤 Hisobim va yangi 💘 Headshot Pro /
    💎 Almaz ishlash. Chiroyli ko'rinishi uchun 2 tadan yonma-yon
    joylashtirilgan.

    🏆 "Top foydalanuvchilar" tugmasi ATAYLAB faqat shu (asosiy) menyuda
    ko'rsatiladi - botning boshqa hech bir bo'limida chiqmaydi."""
    return InlineKeyboardMarkup(
        [
            [
                _ikb("⚙️ Nastroykalar", callback_data=f"{SVC_ALL_PREFIX}:settings"),
                _ikb("✨ Nik yaratish", callback_data=f"{SVC_ALL_PREFIX}:nicks"),
            ],
            [
                _ikb("📰 News", callback_data=NIMAGAP_CB),
                _ikb("👤 Hisobim", callback_data=START_ACCOUNT_CB),
            ],
            [
                _ikb("💘 Headshot Pro", callback_data=HSPRO_INTRO_CB),
                _ikb("💎 Almaz ishlash", callback_data=ALMAZ_ISHLASH_CB),
            ],
            [_ikb("🏆 Top foydalanuvchilar", style="primary", callback_data=TOP_USERS_CB)],
        ]
    )


# ---------- 💎 Almaz ishlash (Referal) ----------

def almaz_page1_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("⬅️ Orqaga", callback_data="start:back"),
                _ikb("➡️ Keyingisi", callback_data=ALMAZ_PAGE2_CB),
            ]
        ]
    )


def almaz_page2_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🔙 Ortga", callback_data=ALMAZ_PAGE1_CB)],
            [_ikb("🔵 💎 Almaz ishlash", style="primary", callback_data=ALMAZ_GO_CB)],
        ]
    )


ALMAZ_WITHDRAW_ACCOUNT_CB = "almazwd:account"
ALMAZ_WITHDRAW_START_CB = "almazwd:start"
ALMAZ_WITHDRAW_CANCEL_CB = "almazwd:cancel"


def almaz_dashboard_keyboard(share_link: str) -> InlineKeyboardMarkup:
    """💎 Almaz ishlash paneli tugmalari - ixcham ko'rinishi uchun asosiy
    tugmalar 2 tadan yonma-yon joylashtirilgan."""
    share_url = f"https://t.me/share/url?url={quote(share_link, safe='')}"
    return InlineKeyboardMarkup(
        [
            [
                _ikb("📤 Referalni ulashish", url=share_url),
                _ikb("👤 Hisobim", callback_data=ALMAZ_ACCOUNT_CB),
            ],
            [_ikb("💎 Almaz yechish", style="primary", callback_data=ALMAZ_WITHDRAW_ACCOUNT_CB)],
            [_ikb("🔙 Ortga", callback_data=ALMAZ_PAGE2_CB)],
        ]
    )


def almaz_account_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("🔙 Ortga", callback_data=ALMAZ_GO_CB)]]
    )


# ---------- 💎 Almaz yechish (Referal berish bo'limi ichidan) ----------

def almaz_withdraw_account_keyboard() -> InlineKeyboardMarkup:
    """💎 jami almaz + "Almazimni yechish" tugmasi ko'rsatiladigan ekran."""
    return InlineKeyboardMarkup(
        [
            [_ikb("💎 Almazimni yechish", style="primary", callback_data=ALMAZ_WITHDRAW_START_CB)],
            [_ikb("🔙 Ortga", callback_data=ALMAZ_GO_CB)],
        ]
    )


def almaz_withdraw_not_enough_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Orqaga", callback_data=ALMAZ_WITHDRAW_ACCOUNT_CB)]]
    )


def almaz_withdraw_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("❌ Bekor qilish", callback_data=ALMAZ_WITHDRAW_CANCEL_CB)]]
    )


# ---------- 💘 Headshot Pro (pullik nastroyka sotib olish) ----------

HSPRO_PRICES_CB = "hspro:prices"
HSPRO_BUY_CB = "hspro:buy"
HSPRO_CANCEL_CB = "hspro:cancel"


def hspro_intro_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("⬅️ Orqaga", callback_data="start:back"),
                _ikb("Keyingisi ➡️", callback_data=HSPRO_PRICES_CB),
            ]
        ]
    )


def hspro_prices_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("⬅️ Orqaga", callback_data=HSPRO_INTRO_CB),
                _ikb("🛒 Sotib olaman", callback_data=HSPRO_BUY_CB),
            ]
        ]
    )


def hspro_payment_method_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🏧 Bankomat orqali", callback_data="hspro:pay:atm")],
            [_ikb("💳 Humo/Uzcard orqali", callback_data="hspro:pay:humo")],
            [_ikb("⬅️ Orqaga", callback_data=HSPRO_PRICES_CB)],
        ]
    )


def hspro_card_keyboard(method: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("✅ Bajarildi", callback_data=f"hspro:done:{method}")],
            [_ikb("⬅️ Orqaga", callback_data=HSPRO_BUY_CB)],
        ]
    )


def hspro_amount_nav_keyboard() -> InlineKeyboardMarkup:
    """💰 'Qancha to'lov qildingiz?' so'ralayotganda chiqadigan
    Orqaga / Bekor qilish tugmalari."""
    return InlineKeyboardMarkup(
        [
            [
                _ikb("⬅️ Orqaga", callback_data=HSPRO_BUY_CB),
                _ikb("❌ Bekor qilish", callback_data=HSPRO_CANCEL_CB),
            ]
        ]
    )


def admin_hspro_review_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("✅ Qabul qilamiz", callback_data=f"hspro_ok:{order_id}"),
                _ikb("❌ Yo'q", callback_data=f"hspro_no:{order_id}"),
            ]
        ]
    )


def hspro_get_settings_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """To'lov qabul qilingandan keyin foydalanuvchiga chiqadigan
    "🔧 Nastroykani olish" tugmasi - bosilsa telefon modeli so'raladi."""
    return InlineKeyboardMarkup(
        [[_ikb("🔧 Nastroykani olish", callback_data=f"hspro_getset:{order_id}")]]
    )


# ---------- 🆕 "🛠️ Barcha xizmatlar" - TO'LIQ INLINE ro'yxat ----------
# MUHIM: bu klaviaturada BIRORTA HAM pastki (Reply) tugma yo'q - hammasi
# inline. Har bir band bosilganda eski (reply tugmali) handlerlar hech
# o'zgartirilmasdan ("shim" orqali) chaqiriladi - shu sabab funksiyalarning
# o'zi ishlashda 100% avvalgidek qoladi.
SVC_ALL_PREFIX = "svcall"

# MUHIM: Foydalanuvchi so'rovi bo'yicha "🛠️ Barcha xizmatlar" ro'yxatidan
# quyidagi bandlar OLIB TASHLANDI: 🎵 Musiqa yaratish, 🖼️ Rasm Yasash,
# 🎬 Video Yasash, 🎁 Giftlar va 🛒 Free Fire Do'koni. Ularning kodi
# (BTN_MAIN_RASM, BTN_MAIN_VIDEO va h.k.) va tegishli handlerlar hech
# narsa o'chirilmagan - faqat shu ro'yxatdan olib tashlandi, kerak bo'lsa
# pastdagi izohlangan qatorlarni qaytarish mumkin.
# MUHIM: Foydalanuvchi so'rovi bo'yicha "🛠️ Barcha xizmatlar" ro'yxatidagi
# BARCHA bandlar OLIB TASHLANDI (ro'yxat bo'shatildi). Har bir bandning
# kodi (BTN_M2_SERVICES, BTN_M2_SETTINGS va h.k.) va tegishli handlerlar
# hech narsa o'chirilmagan - faqat shu ro'yxatdan olib tashlandi, kerak
# bo'lsa pastdagi izohlangan qatorlarni qaytarish mumkin.
_ALL_SERVICES_ITEMS = [
    # (BTN_M2_SERVICES, f"{SVC_ALL_PREFIX}:services"),
    # (BTN_M2_SETTINGS, f"{SVC_ALL_PREFIX}:settings"),
    # (BTN_M2_NICKS, f"{SVC_ALL_PREFIX}:nicks"),
    # (BTN_MAIN_RASM, f"{SVC_ALL_PREFIX}:rasm"),
    # (BTN_MAIN_VIDEO, f"{SVC_ALL_PREFIX}:video"),
    # (BTN_MAIN_MUSIC, f"{SVC_ALL_PREFIX}:music"),
    # (BTN_STORE, f"{SVC_ALL_PREFIX}:store"),
    # (BTN_M2_PAYMENTS, f"{SVC_ALL_PREFIX}:payments"),
    # (BTN_MINI_GAMES, f"{SVC_ALL_PREFIX}:games"),
    # (BTN_GIFTS, f"{SVC_ALL_PREFIX}:gifts"),
    # (BTN_PRO_SUB, f"{SVC_ALL_PREFIX}:prosub"),
    # (BTN_WITHDRAW_WIN, f"{SVC_ALL_PREFIX}:withdrawwin"),
    # (BTN_ORDERS_CHANNEL, f"{SVC_ALL_PREFIX}:orders"),
    # (BTN_GIFT_ORDER, f"{SVC_ALL_PREFIX}:giftorder"),
    # (BTN_M2_DIAMONDS, f"{SVC_ALL_PREFIX}:diamonds"),
    # (BTN_WITHDRAW, f"{SVC_ALL_PREFIX}:withdraw"),
    # (BTN_WEBSITE, f"{SVC_ALL_PREFIX}:turnirlar"),
]


def all_services_inline_keyboard() -> InlineKeyboardMarkup:
    # MUHIM: Foydalanuvchi so'rovi bo'yicha "🗺 Free Fire Portal 🚀" tugmasi
    # ro'yxatdan olib tashlandi. Kodi (BTN_PORTAL, WEBAPP_URL) o'chirilmagan -
    # kerak bo'lsa quyidagi qatorni qayta izohdan chiqarib qaytarish mumkin.
    rows = []
    # rows = [[_ikb(BTN_PORTAL, web_app=WebAppInfo(url=WEBAPP_URL))]]

    # Foydalanuvchi so'rovi bo'yicha - 2 tadan emas, 4 tadan yonma-yon
    # (bitta qatorda 4 ta tugma) qilib joylanadi.
    chunk_size = 4
    row: list = []
    for text, cb in _ALL_SERVICES_ITEMS:
        row.append(_ikb(text, callback_data=cb))
        if len(row) == chunk_size:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    # 📬 Savollar (FAQ) - allaqachon mavjud "svc:faq" pattern'i orqali
    # ishlaydigan conversation handler bor, shu sabab shu callback_data
    # qayta ishlatiladi (qo'shimcha handler shart emas).
    rows.append([_ikb(BTN_M2_FAQ, callback_data="svc:faq")])

    return InlineKeyboardMarkup(rows)


# ---------- 🎮 "Nima gap?" bo'limi (Free Fire turnirlar / akkauntlar) ----------

NIMAGAP_TOURNAMENTS_CB = "nimagap:tournaments"
NIMAGAP_ACCOUNTS_CB = "nimagap:accounts"
FFTOUR_PREFIX = "fftour"

# (slot_key, tugma matni) - tartib shu bo'yicha ko'rsatiladi.
TOURNAMENT_SLOTS = [
    ("today", "🔥 Bugungi turnirlar"),
    ("tomorrow", "📅 Ertangi turnirlar"),
    ("2days", "📆 2 kundan keyingi"),
    ("3days", "🗓 3 kundan keyingi"),
    ("1week", "⭐ 1 haftadan keyingi"),
]
TOURNAMENT_SLOT_LABELS = dict(TOURNAMENT_SLOTS)


def nimagap_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb(BTN_WEBSITE, style="success", callback_data=NIMAGAP_TOURNAMENTS_CB),
                _ikb("🎮 Free Fire akkauntlar", style="success", callback_data=NIMAGAP_ACCOUNTS_CB),
            ],
            [_ikb("⬅️ Bosh menyu", callback_data="start:back")],
        ]
    )


def fftournament_slots_keyboard() -> InlineKeyboardMarkup:
    rows = [[_ikb(label, callback_data=f"{FFTOUR_PREFIX}:{key}")] for key, label in TOURNAMENT_SLOTS]
    rows.append([_ikb("⬅️ Orqaga", callback_data=NIMAGAP_CB)])
    return InlineKeyboardMarkup(rows)


# ---------- 🏆 Free Fire Turnirlar (asosiy pastki tugma, ochiq ro'yxat) ----------
# Bu "🏆 Free Fire Turnirlar" pastki (reply) tugmasi bosilganda ochiladigan
# bo'lim uchun: admin xohlagancha turnir qo'shishi mumkin (kuniga 3-4 tasi
# bo'lsa ham), har biri o'z formati (3/3, 1/1 va h.k.) bilan ko'rsatiladi.

TURNIRADMIN_ADD_CB = "turniradmin:add"


def turnir_emoji_for_index(index: int) -> str:
    """Har bir turnir uchun ro'yxatda chiroyli, o'zgaruvchan emoji."""
    icons = ["🥇", "🥈", "🥉", "🏅", "🔥", "⚡️", "🎯", "🎮"]
    return icons[index % len(icons)]


def turnirlar_list_keyboard(turnirlar: list, is_admin: bool = False) -> InlineKeyboardMarkup:
    rows = []
    for i, t in enumerate(turnirlar):
        day = (t.get("day_label") or "").strip() or "Kun belgilanmagan"
        fmt = (t.get("format_text") or "").strip()
        label = f"{turnir_emoji_for_index(i)} {day}"
        if fmt:
            label += f" • {fmt}"
        rows.append([_ikb(label, callback_data=f"turnir:open:{t['id']}")])
    if is_admin:
        rows.append([_ikb("➕ Turnir qo'shish", callback_data=TURNIRADMIN_ADD_CB)])
    return InlineKeyboardMarkup(rows)


def turnirlar_detail_keyboard(turnirlar: list, index: int, is_admin: bool = False) -> InlineKeyboardMarkup:
    rows = []
    nav_row = []
    if index > 0:
        nav_row.append(_ikb("⬅️ Oldingi turnir", callback_data=f"turnir:nav:{index - 1}"))
    if index < len(turnirlar) - 1:
        nav_row.append(_ikb("Keyingi turnir ➡️", callback_data=f"turnir:nav:{index + 1}"))
    if nav_row:
        rows.append(nav_row)
    rows.append([_ikb("📋 Turnirlar ro'yxati", callback_data="turnir:list")])
    if is_admin and 0 <= index < len(turnirlar):
        rows.append(
            [_ikb("🗑 Ushbu turnirni o'chirish", callback_data=f"turniradmin:del:{turnirlar[index]['id']}")]
        )
    if is_admin:
        rows.append([_ikb("➕ Turnir qo'shish", callback_data=TURNIRADMIN_ADD_CB)])
    return InlineKeyboardMarkup(rows)


# ---------- 🗂 Admin: Turnir/Akkaunt boshqaruvi ----------

def ff_admin_panel_keyboard(tournament_status: dict, account_added: bool) -> InlineKeyboardMarkup:
    rows = []
    for slot, label in TOURNAMENT_SLOTS:
        mark = "✅" if tournament_status.get(slot) else "❌"
        rows.append(
            [_ikb(f"{mark} {label}", callback_data=f"ffadmin:tour:{slot}")]
        )
    acc_mark = "✅" if account_added else "❌"
    rows.append([_ikb(f"{acc_mark} 🎮 Free Fire akkaunt", callback_data="ffadmin:acc")])
    rows.append([_ikb("🔙 Yopish", callback_data="ffadmin:close")])
    return InlineKeyboardMarkup(rows)


def ffadmin_tour_actions_keyboard(slot: str, added: bool) -> InlineKeyboardMarkup:
    rows = [[_ikb("➕ Qo'shish / Tahrirlash", callback_data=f"ffadmin:touradd:{slot}")]]
    if added:
        rows.append([_ikb("🗑 O'chirish", callback_data=f"ffadmin:tourdel:{slot}")])
    rows.append([_ikb("⬅️ Orqaga", callback_data="ffadmin:panel")])
    return InlineKeyboardMarkup(rows)


def ffadmin_acc_actions_keyboard(added: bool) -> InlineKeyboardMarkup:
    rows = [[_ikb("➕ Qo'shish / Tahrirlash", callback_data="ffadmin:accadd")]]
    if added:
        rows.append([_ikb("🗑 O'chirish", callback_data="ffadmin:accdel")])
    rows.append([_ikb("⬅️ Orqaga", callback_data="ffadmin:panel")])
    return InlineKeyboardMarkup(rows)


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """MUHIM (foydalanuvchi so'rovi bo'yicha): ESKI pastki (Reply) menyu
    endi ADMIN uchun ham, oddiy foydalanuvchi uchun ham BUTUNLAY
    ko'RSATILMAYDI. Butun botda navigatsiya endi FAQAT yangi menyu
    (start_inline_keyboard()) va har bir bo'lim tagidagi qizil
    "🔐 Yordam" tugmasi orqali amalga oshiriladi.

    Funksiya o'zi o'chirilmagan (chaqiradigan o'nlab joy buzilmasligi
    uchun) - shunchaki endi har doim ReplyKeyboardRemove() qaytaradi,
    ya'ni mavjud bo'lsa eski pastki tugmalar oynasini olib tashlaydi."""
    return ReplyKeyboardRemove()


# ---------- 🌐 Til tanlash ----------

def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("🇺🇿 O'zbek tili", callback_data="lang:uz"),
                _ikb("🇷🇺 Русский язык", callback_data="lang:ru"),
            ]
        ]
    )


# ---------- Majburiy obuna ----------

def subscription_keyboard() -> InlineKeyboardMarkup:
    """Majburiy obuna kanallari - har biri o'z emojisi bilan, alohida
    qatorda (chiroyliroq va o'qish oson bo'lishi uchun), ostida
    "✅ Obuna bo'ldim" (tekshirish) tugmasi."""
    rows = [
        [_ikb(f"{ch.get('emoji', '📡')} {ch['name']}", url=f"https://t.me/{ch['username']}")]
        for ch in REQUIRED_CHANNELS
    ]
    rows.append([_ikb("✅ Obuna bo'ldim", callback_data="check_sub")])
    return InlineKeyboardMarkup(rows)


# ---------- Pro/Bot o'yinchi savoli va guruhga qo'shish ----------

def player_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("🏆 Pro o'yinchiman", callback_data="player:pro"),
                _ikb("🤖 Bot o'yinchiman", callback_data="player:bot"),
            ]
        ]
    )


def add_to_group_keyboard(bot_username: str) -> InlineKeyboardMarkup:
    url = f"https://t.me/{bot_username}?startgroup=true"
    return InlineKeyboardMarkup(
        [[_ikb("➕ Botni guruhga qo'shish", url=url)]]
    )


# ---------- Foydali web sayt ----------

def website_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("🌐 Saytga o'tish", web_app=WebAppInfo(url=WEBSITE_URL))]]
    )


# ---------- 🗺 Free Fire Portal (Mini App) ----------

def mini_app_portal_keyboard(bot_username: str = "") -> InlineKeyboardMarkup:
    """NovaPin uslubidagi Mini App tugmasi + kanal + qo'llanma."""
    rows = [
        [_ikb("🗺 Free Fire Portal 🚀", web_app=WebAppInfo(url=WEBAPP_URL))],
        [_ikb("📢 Kanal", url=NEWS_CHANNEL_URL)],
        [_ikb("📖 Qo'llanma", callback_data="svc:guides")],
    ]
    return InlineKeyboardMarkup(rows)


def portal_button_row() -> list:
    """Boshqa menyularga qo'shish uchun bitta qatorlik Portal tugmasi."""
    return [_ikb("🗺 Free Fire Portal 🚀", web_app=WebAppInfo(url=WEBAPP_URL))]


# ---------- Free Fire qo'shiq ----------

def music_keyboard(music_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("🎧 Qo'shiqni tinglash", url=music_url)]]
    )


# ---------- Nastroykalar (telefon: brendlar -> modellar) ----------

def brands_keyboard() -> InlineKeyboardMarkup:
    rows = []
    brands = list(PHONES.keys())
    for i in range(0, len(brands), 2):
        chunk = brands[i:i + 2]
        rows.append(
            [_ikb(b, callback_data=f"brand:{b}") for b in chunk]
        )
    # QIZIL "⬅️ Orqaga" tugmasi - Bosh menyuga qaytaradi. Bu tugma
    # borligi sababli avtomatik "🎮 Free Fire menyu" tugmasi endi
    # bu yerga QO'SHILMAYDI (_has_nav_button uni aniqlaydi).
    rows.append([_ikb("⬅️ Orqaga", style="danger", callback_data="start:back")])
    return InlineKeyboardMarkup(rows)


def models_keyboard(brand: str) -> InlineKeyboardMarkup:
    rows = []
    models = PHONES.get(brand, [])
    for i in range(0, len(models), 2):
        chunk = models[i:i + 2]
        rows.append(
            [_ikb(m, callback_data=f"model:{m}") for m in chunk]
        )
    # QIZIL "⬅️ Orqaga" tugmasi - brendlar ro'yxatiga qaytaradi.
    rows.append([_ikb("⬅️ Orqaga", style="danger", callback_data="back_to_brands")])
    return InlineKeyboardMarkup(rows)


def model_back_keyboard(brand: str) -> InlineKeyboardMarkup:
    # QIZIL "⬅️ Orqaga" tugmasi - shu brendning modellar ro'yxatiga
    # qaytaradi (ilgari bu funksiya None qaytarardi va umuman tugma
    # ko'rinmasdi - shu sabab "orqaga" tugmasi ishlamayotgandek tuyulardi).
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Orqaga", style="danger", callback_data=f"brand:{brand}")]]
    )


# ---------- 👑 Admin: Nastroyka qo'shish (brend -> model -> kontent turi) ----------

BTN_NASTROYKA_ADD = "➕ NASTROYKA QO'SHISH"

NASTROYKA_CONTENT_TYPES = [
    ("text", "📝 TEXT"),
    ("photo", "🖼 RASM"),
    ("video", "🎬 VIDEO"),
    ("phototext", "📦 TEXT + RASM"),
    ("videotext", "🎬 VIDEO + TEXT"),
]


def nastroyka_admin_brands_keyboard() -> InlineKeyboardMarkup:
    rows = []
    brands = list(PHONES.keys())
    for i in range(0, len(brands), 2):
        chunk = brands[i:i + 2]
        rows.append(
            [_ikb(b, callback_data=f"nadmin:brand:{b}") for b in chunk]
        )
    rows.append([_ikb("🔙 Yopish", callback_data="nadmin:close")])
    return InlineKeyboardMarkup(rows)


def nastroyka_admin_models_keyboard(brand: str) -> InlineKeyboardMarkup:
    rows = []
    models = PHONES.get(brand, [])
    for i in range(0, len(models), 2):
        chunk = models[i:i + 2]
        row = []
        for m in chunk:
            has_content = db.get_nastroyka_content(m) is not None
            mark = "✅" if has_content else "❌"
            row.append(_ikb(f"{mark} {m}", callback_data=f"nadmin:model:{m}"))
        rows.append(row)
    rows.append([_ikb("⬅️ Orqaga", callback_data="nadmin:back_brands")])
    return InlineKeyboardMarkup(rows)


def nastroyka_admin_type_keyboard(model_name: str, has_content: bool) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(NASTROYKA_CONTENT_TYPES), 2):
        chunk = NASTROYKA_CONTENT_TYPES[i:i + 2]
        rows.append(
            [_ikb(label, callback_data=f"nadmin:type:{key}") for key, label in chunk]
        )
    if has_content:
        rows.append([_ikb("🗑 O'chirish", callback_data="nadmin:delete")])
    rows.append([_ikb("⬅️ Orqaga", callback_data="nadmin:back_models")])
    return InlineKeyboardMarkup(rows)


# ---------- Planshet nastroykalari ----------

def tablet_brands_keyboard() -> InlineKeyboardMarkup:
    rows = []
    brands = list(TABLETS.keys())
    for i in range(0, len(brands), 2):
        chunk = brands[i:i + 2]
        rows.append(
            [_ikb(b, callback_data=f"tbrand:{b}") for b in chunk]
        )
    rows.append([_ikb("⬅️ Bosh menyu", callback_data="start:back")])
    return InlineKeyboardMarkup(rows)


def tablet_models_keyboard(brand: str) -> InlineKeyboardMarkup:
    rows = []
    models = TABLETS.get(brand, [])
    for i in range(0, len(models), 2):
        chunk = models[i:i + 2]
        rows.append(
            [_ikb(m[0], callback_data=f"tmodel:{m[0]}") for m in chunk]
        )
    rows.append([_ikb("⬅️ Orqaga", callback_data="back_to_tbrands")])
    return InlineKeyboardMarkup(rows)


def tablet_model_back_keyboard(brand: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Modellarga qaytish", callback_data=f"tbrand:{brand}")]]
    )


# ---------- Niklar ----------

def nicknames_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("👦 Erkaklar niklari", callback_data="nick:male"),
                _ikb("👧 Qizlar niklari", callback_data="nick:female"),
            ]
        ]
    )


# ---------- Qo'llanmalar ----------

def guides_keyboard() -> InlineKeyboardMarkup:
    rows = []
    items = list(GUIDES.items())
    for i in range(0, len(items), 2):
        chunk = items[i:i + 2]
        rows.append(
            [_ikb(v["title"], callback_data=f"guide:{k}") for k, v in chunk]
        )
    return InlineKeyboardMarkup(rows)


def guide_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Qo'llanmalarga qaytish", callback_data="back_to_guides")]]
    )


# ---------- 🔓 Free Fire Hack (Proxy + Cheat + FF ID birlashtirilgan) ----------

def hack_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🛰️ Proxy server", callback_data="hack:proxy")],
            [_ikb("🛠️ Cheat va panellar", callback_data="hack:cheat")],
            [_ikb("🕹️ Mening FF ID'im", callback_data="hack:ffid")],
        ]
    )


def hack_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Orqaga", callback_data="hack:back")]]
    )


# ---------- Almaz sotib olish ----------

def diamonds_entry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("👤 Admin orqali olish", callback_data="dia:admin"),
                _ikb("🤖 Bot orqali olish", callback_data="dia:bot"),
            ]
        ]
    )


def diamonds_admin_keyboard(admin_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("💬 Admin bilan bog'lanish", url=f"https://t.me/{admin_username}")],
            [_ikb("⬅️ Orqaga", callback_data="dia:back")],
        ]
    )


def diamonds_packages_keyboard() -> InlineKeyboardMarkup:
    rows = []
    items = [{**p, "type": "package"} for p in PACKAGES]
    for i in range(0, len(items), 2):
        chunk = items[i:i + 2]
        rows.append(
            [_ikb(button_label(it), callback_data=f"pkg:{it['key']}") for it in chunk]
        )
    sub_items = [{**s, "type": "subscription"} for s in SUBSCRIPTIONS]
    for i in range(0, len(sub_items), 2):
        chunk = sub_items[i:i + 2]
        rows.append(
            [_ikb(button_label(it), callback_data=f"pkg:{it['key']}") for it in chunk]
        )
    rows.append([_ikb("⬅️ Orqaga", callback_data="dia:back")])
    return InlineKeyboardMarkup(rows)


def package_detail_keyboard(key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🛒 Sotib olish", callback_data=f"buy:{key}")],
            [_ikb("⬅️ Orqaga", callback_data="dia:bot")],
        ]
    )


def insufficient_balance_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("💰 Mening hisobim", callback_data="go_account")]]
    )


# ---------- Hisobim ----------

def account_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("👤 Admin orqali to'ldirish", callback_data="acc:admin"),
                _ikb("💳 Humo/Uzcard orqali to'ldirish", callback_data="acc:card"),
            ],
            [_ikb("🎁 Bonus", callback_data="acc:bonus")],
            # QIZIL "⬅️ Orqaga" tugmasi - Bosh menyuga qaytaradi.
            [_ikb("⬅️ Orqaga", style="danger", callback_data="start:back")],
        ]
    )


def account_admin_keyboard(admin_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("💬 Admin bilan bog'lanish", url=f"https://t.me/{admin_username}")],
            [_ikb("⬅️ Orqaga", style="danger", callback_data="acc:back")],
        ]
    )


def paid_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("✅ To'lov qildim", callback_data="topup:paid")]]
    )


def admin_topup_review_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("✅ Ha", callback_data=f"topup_ok:{request_id}"),
                _ikb("❌ Yo'q", callback_data=f"topup_no:{request_id}"),
            ]
        ]
    )


def admin_order_review_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("✅ Yubordim", callback_data=f"order_sent:{order_id}")]]
    )


# ---------- Admin: matnlarni tahrirlash ----------

def edit_texts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("🎧 Yordam matni", callback_data="edittext:help_text"),
                _ikb("🛠️ Cheat matni", callback_data="edittext:cheat_text"),
            ],
            [
                _ikb("🛰️ Proxy matni", callback_data="edittext:proxy_text"),
                _ikb("🎬 Free Fire 2017", callback_data="edittext:ff2017_content"),
            ],
        ]
    )


# ---------- 📲 Shaxsiy nastroyka (Pullik/Bepul) ----------

def custom_entry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("💰 Pullik nastroyka", callback_data="custom:paid")],
            [_ikb("🆓 Bepul nastroyka", callback_data="custom:free")],
        ]
    )


def paid_tiers_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🎯 80% Headshot", callback_data="paidtier:hs80")],
            [_ikb("🎯 97% Headshot", callback_data="paidtier:hs97")],
            [_ikb("⬅️ Orqaga", callback_data="custom:back")],
        ]
    )


def paid_tier_detail_keyboard(key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🛒 Xarid qilish", callback_data=f"paidbuy:{key}")],
            [_ikb("⬅️ Orqaga", callback_data="custom:paid")],
        ]
    )


def paid_disclaimer_keyboard(key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("✅ Roziman", callback_data=f"paidagree:{key}")]]
    )


def custom_admin_keyboard(
    user_id: int, label: str = "📤 Nastroyka yuborish", order_kind: str = "nastroyka"
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb(label, callback_data=f"customreply:{order_kind}:{user_id}")]]
    )


# ---------- 📢 Buyurtmalar kanali ----------

def orders_channel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("📢 Kanalga o'tish", url=f"https://t.me/{ORDERS_CHANNEL_USERNAME}")]]
    )


# ---------- 📬 Savollar (FAQ) ----------

def faq_admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("💬 Javob berish", callback_data=f"faqreply:{user_id}")]]
    )


# ---------- 🧠 Savol va Javob (Quiz) ----------

def quiz_intro_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("▶️ Boshladik", callback_data="quiz_begin")]]
    )


def quiz_options_keyboard(question_index: int, options: list) -> InlineKeyboardMarkup:
    rows = []
    for i, opt in enumerate(options):
        rows.append([_ikb(opt, callback_data=f"quiz:{question_index}:{i}")])
    return InlineKeyboardMarkup(rows)


# ---------- 🛠 Admin buyrug'i (qo'lda pul/almaz berish) ----------

def admin_credit_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("💎 Almaz berish", callback_data="credittype:diamond"),
                _ikb("💰 Pul berish", callback_data="credittype:money"),
            ],
            [
                _ikb("🚫 Foydalanuvchini bloklash", callback_data="credittype:block"),
            ],
        ]
    )


# ---------- 🎁 Hammaga sovg'a (barcha foydalanuvchilarga birdaniga) ----------

def gift_all_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("💎 Almaz berish", callback_data="giftall:diamond"),
                _ikb("💰 Pul berish", callback_data="giftall:money"),
            ]
        ]
    )


def gift_all_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("✅ Ha, yubor", callback_data="giftall_confirm"),
                _ikb("❌ Bekor qilish", callback_data="giftall_cancel"),
            ]
        ]
    )


# ---------- 🗑 Hammadan almazni yechish (ommaviy, xabarsiz) ----------

DEDUCT_ALL_CONFIRM_YES_CB = "deductall:yes"
DEDUCT_ALL_CONFIRM_NO_CB = "deductall:no"


def deduct_all_diamonds_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("✅ Ha, hammadan yechilsin", style="primary", callback_data=DEDUCT_ALL_CONFIRM_YES_CB),
                _ikb("❌ Bekor qilish", callback_data=DEDUCT_ALL_CONFIRM_NO_CB),
            ]
        ]
    )


# ---------- 💎 Almaz yechish ----------

def withdraw_amount_keyboard(amount: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb(f"💎 {amount}", callback_data=f"withdraw_confirm:{amount}")]]
    )


# ---------- 💎 Almaz yechish (🆕 yangi oqim: avval "Hisobim", pastida "Yechish") ----------

def withdraw_account_keyboard() -> InlineKeyboardMarkup:
    """"Hisobim" (joriy almaz balansi) matni ostida chiqadigan
    "💎 Yechish" va "⬅️ Orqaga" inline tugmalari."""
    return InlineKeyboardMarkup(
        [
            [_ikb("💎 Yechish", callback_data="withdraw:start")],
            [_ikb("⬅️ Orqaga", callback_data=START_SERVICES_CB)],
        ]
    )


def withdraw_cancel_keyboard() -> InlineKeyboardMarkup:
    """Free Fire ID / miqdor so'ralayotganda chiqadigan "❌ Bekor qilish"
    tugmasi - foydalanuvchi /bekor yozmasdan ham orqaga qaytishi mumkin."""
    return InlineKeyboardMarkup(
        [[_ikb("❌ Bekor qilish", callback_data="withdraw:cancel")]]
    )


def withdraw_not_enough_back_keyboard() -> InlineKeyboardMarkup:
    """Almaz yetarli bo'lmaganda "Hisobim" ko'rinishiga qaytish tugmasi."""
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Orqaga", callback_data="withdraw:back")]]
    )


def withdraw_admin_review_keyboard(user_id: int, amount: int, ff_id: str) -> InlineKeyboardMarkup:
    """Adminga boradigan xabar ostidagi "✅ Yubordim" tugmasi - admin buni
    bosgach, foydalanuvchiga "almazlaringiz yuborildi" xabari boradi."""
    return InlineKeyboardMarkup(
        [[_ikb("✅ Yubordim", callback_data=f"withdrawsent:{user_id}:{amount}:{ff_id}")]]
    )


# ---------- 🎬 Free Fire 2017 ----------

BTN_FF2017 = "🎬 Free Fire 2017"


# ---------- Cheat/Proxy uchun kanal havolasi ----------

def hack_content_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("📢 @freefirechitpanel", url="https://t.me/freefirechitpanel")],
            [_ikb("⬅️ Orqaga", callback_data="hack:back")],
        ]
    )


# ============================================================================
# 🎮 Free Fire (yangi bosh menyu bo'limi)
# ============================================================================

def ff_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("📱 Telefon nastroyka", callback_data="ffmenu:phone")],
            [_ikb("📲 Planshet nastroyka", callback_data="ffmenu:tablet")],
            [_ikb("💻 PC nastroyka", callback_data="ffmenu:pc")],
            [_ikb("🎮 Nik yaratish", callback_data="ffmenu:nick")],
        ]
    )


def back_to_ff_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Bosh menyu", callback_data="start:back")]]
    )


# ---------- 💻 PC nastroykalari (20 ta model, brendsiz to'g'ridan-to'g'ri) ----------

def pc_keyboard() -> InlineKeyboardMarkup:
    rows = []
    names = [m[0] for m in PC_MODELS]
    for i in range(0, len(names), 2):
        chunk = names[i:i + 2]
        rows.append(
            [_ikb(n, callback_data=f"pc:{n}") for n in chunk]
        )
    rows.append([_ikb("⬅️ Bosh menyu", callback_data="start:back")])
    return InlineKeyboardMarkup(rows)


def pc_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ PC modellariga qaytish", callback_data="back_to_pc")]]
    )


# ---------- 🎮 Nik yaratish (orqaga) ----------

def nick_creation_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Bosh menyu", callback_data="start:back")]]
    )


# ============================================================================
# 🛠️ Xizmatlar (yangi bosh menyu bo'limi)
# ============================================================================

def services_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🎁 Bonuslar", callback_data="svc:bonus")],
            [_ikb("💳 To'lov qilish", callback_data="svc:pay")],
            [_ikb("📬 Savollar (FAQ)", callback_data="svc:faq")],
            [_ikb("📚 Qo'llanmalar", callback_data="svc:guides")],
            [_ikb("📰 Yangiliklar", callback_data="svc:news")],
            [_ikb("🔧 Boshqa xizmatlar", callback_data="svc:other")],
        ]
    )


def back_to_services_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Xizmatlar menyusi", callback_data="back_to_services")]]
    )


def services_bonus_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🧠 Savol-javob (Tekin almaz)", callback_data="svcbonus:quiz")],
            [_ikb("🎁 Kunlik bonus", callback_data="svcbonus:daily")],
            [_ikb("⬅️ Xizmatlar menyusi", callback_data="back_to_services")],
        ]
    )


def services_other_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🗺 Free Fire Portal 🚀", web_app=WebAppInfo(url=WEBAPP_URL))],
            [_ikb("🎧 Yordam", callback_data="svcother:help")],
            [_ikb("🏆 Turnirlar / Sayt", callback_data="svcother:website")],
            [_ikb("🎵 Free Fire qo'shiq", callback_data="svcother:music")],
            [_ikb("🔓 Maxsus xizmat", callback_data="svcother:hack")],
            [_ikb("⚠️ Shaxsiy nastroyka", callback_data="svcother:custom")],
            [_ikb("🎬 Free Fire 2017", callback_data="svcother:ff2017")],
            [_ikb("⬅️ Xizmatlar menyusi", callback_data="back_to_services")],
        ]
    )


def back_to_services_other_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Orqaga", callback_data="back_to_svcother")]]
    )


def website_service_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🏆 Turnirlar / Yangiliklar sayti", web_app=WebAppInfo(url=WEBAPP_URL))],
            [_ikb("⬅️ Orqaga", callback_data="back_to_svcother")],
        ]
    )


def music_service_keyboard(music_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🎧 Qo'shiqni tinglash", url=music_url)],
            [_ikb("⬅️ Orqaga", callback_data="back_to_svcother")],
        ]
    )


# ============================================================================
# 👤 Profil (yangi bosh menyu bo'limi)
# ============================================================================

def profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("💰 Mening hisobim", callback_data="profile:account")],
            [_ikb("💎 Almaz yechish", callback_data="profile:withdraw")],
        ]
    )


# ============================================================================
# 🆕 Yangi bosh menyu bo'limlari uchun inline klaviaturalar
# (💎 Almaz olish / 🛍 Xizmatlar / ⚙️ Nastroykalar / 🎉 Free Fire Niklar /
#  💰 To'lov usullari)
# ============================================================================

# ---------- 💎 Almaz olish ----------

def diamonds_get_keyboard() -> InlineKeyboardMarkup:
    # MUHIM: Foydalanuvchi so'rovi bo'yicha "🆓 Tekin Almaz" tugmasi olib
    # tashlandi (kodi/handleri o'chirilmagan, faqat shu yerda
    # ko'rsatilmayapti).
    return InlineKeyboardMarkup(
        [
            [
                _ikb("🆓 Tekin Almaz", callback_data="diaget:free"),
                _ikb("💎 Almaz sotib olish", callback_data="diaget:buy"),
            ]
        ]
    )


# ---------- ⚙️ Nastroykalar (yangi asosiy bo'lim) ----------

def new_settings_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("📱 Telefon nastroykalari", callback_data="newset:phone"),
                _ikb("📲 Planshet nastroykalari", callback_data="newset:tablet"),
            ],
            [
                _ikb("🖥 PC nastroykalari", callback_data="newset:pc"),
                _ikb("🎁✨ Maxsus nastroykalar", callback_data="newset:premium"),
            ],
        ]
    )


def new_settings_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Orqaga", callback_data="newset:back")]]
    )


# ---------- 🎉 Free Fire Niklar (yangi asosiy bo'lim) ----------

def new_nicks_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("🎮 Gamer Niklar", callback_data="newnick:gamer"),
                _ikb("👑 Super Niklar", callback_data="newnick:super"),
            ],
            [
                _ikb("🔥 Pro Niklar", callback_data="newnick:pro"),
                _ikb("⚡ Top Niklar", callback_data="newnick:top"),
            ],
            [
                _ikb("✨ Chiroyli Niklar", callback_data="newnick:chiroyli"),
                _ikb("🛠 Nik Yasash", callback_data="ffmenu:nick"),
            ],
            # QIZIL "⬅️ Orqaga" tugmasi - Bosh menyuga qaytaradi.
            [_ikb("⬅️ Orqaga", style="danger", callback_data="start:back")],
        ]
    )


def new_nicks_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Orqaga", style="danger", callback_data="newnick:back")]]
    )


# ---------- 🛍 Xizmatlar (yangi asosiy bo'lim) ----------

def new_services_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🗺 Free Fire Portal 🚀", web_app=WebAppInfo(url=WEBAPP_URL))],
            [
                _ikb("🎮 Free Fire 2017", callback_data="newsvc:ff2017"),
                _ikb("🏆 Free Fire Turnirlari", callback_data="newsvc:tournament"),
            ],
            [
                _ikb("🌐 Proxy Server", callback_data="newsvc:proxy"),
                _ikb("🆔 FF IDM", callback_data="newsvc:ffidm"),
            ],
            [
                _ikb("💀 Cheat Panel", callback_data="newsvc:cheat"),
                _ikb("📰 Free Fire Yangiliklari", callback_data="newsvc:news"),
            ],
            [
                _ikb("🎵 Free Fire Qo'shiqlari", callback_data="newsvc:music"),
            ],
        ]
    )


def newsvc_portal_keyboard() -> InlineKeyboardMarkup:
    """🏆 Turnirlar / 📰 Yangiliklar uchun Free Fire Portal (Web App) tugmasi."""
    return InlineKeyboardMarkup(
        [
            [_ikb("🗺 Free Fire Portal 🚀", web_app=WebAppInfo(url=WEBAPP_URL))],
            [_ikb("⬅️ Orqaga", callback_data="newsvc:back")],
        ]
    )


def service_channel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("📢 Kanalga qo'shilish", url="https://t.me/freefirepanelchit")],
            [_ikb("⬅️ Orqaga", callback_data="newsvc:back")],
        ]
    )


# ---------- 🎁 Sovg'alar (bosh menyu tugmasi) ----------

def gifts_keyboard() -> InlineKeyboardMarkup:
    # MUHIM: Foydalanuvchi so'rovi bo'yicha "🆓 Tekin almaz" tugmasi olib
    # tashlandi (kodi/handleri o'chirilmagan, faqat shu yerda
    # ko'rsatilmayapti).
    return InlineKeyboardMarkup(
        [
            [_ikb("🆓 Tekin almaz", callback_data="gift:free_diamond")],
            [_ikb("💵 Pul bonusi", callback_data="gift:money_bonus")],
            [_ikb("🌙 Almaz bonusi", callback_data="gift:diamond_bonus")],
        ]
    )


# ---------- 💰 To'lov usullari (yangi asosiy bo'lim) ----------

def payments_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("👤 Admin orqali to'ldirish", callback_data="pay:admin"),
                _ikb("💳 Humo/Uzcard orqali to'ldirish", callback_data="pay:card"),
            ],
        ]
    )


def payments_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Orqaga", callback_data="pay:back")]]
    )


# ---------- 👛 Hisobim -> 💰 To'lov usullari ----------

def my_account_keyboard() -> InlineKeyboardMarkup:
    # MUHIM: Foydalanuvchi so'rovi bo'yicha "💰 To'lov usullari" tugmasi
    # olib tashlandi. Kodi (myacc:pay callback va handler) o'chirilmagan -
    # kerak bo'lsa quyidagi qatorni qayta izohdan chiqarib qaytarish mumkin.
    return InlineKeyboardMarkup([])
    # return InlineKeyboardMarkup(
    #     [[_ikb("💰 To'lov usullari", callback_data="myacc:pay")]]
    # )


# ---------- 👑 Pro obuna ----------

def pro_sub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("💳 Tarifni sotib olish", callback_data="prosub:buy")]]
    )


# ---------- 👑 Pro obuna FAOLLASHGANDAN KEYINGI maxsus bo'lim ----------
# Barcha tugmalar QIZIL (danger/red) rangda chiqadi.

def pro_sub_active_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🇧🇷 Brazillian nastroyka", style="danger", callback_data="prosec:brazilian")],
            [_ikb("✨ Super nik", style="danger", callback_data="prosec:superik")],
            [_ikb("🎁 Sirli sovg'a", style="danger", callback_data="prosec:sirli")],
            [_ikb("🏆 Mukofot", style="danger", callback_data="prosec:mukofot")],
            [_ikb("🎬 AI video yasash", style="danger", callback_data="prosec:aivideo")],
            [_ikb("🖼️ AI rasm yasash", style="danger", callback_data="prosec:airasm")],
        ]
    )


def pro_section_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Pro obuna bo'limi", style="danger", callback_data="prosec:back")]]
    )


def pro_section_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Bekor qilish", style="danger", callback_data="prosec:back")]]
    )


def pro_secret_gift_keyboard(admin_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("💬 Admin bilan bog'lanish", url=f"https://t.me/{admin_username}")],
            [_ikb("⬅️ Pro obuna bo'limi", style="danger", callback_data="prosec:back")],
        ]
    )


# ---------- 🖼️ Rasm Yasash ----------

def rasm_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🔥 Oddiy Rasm", callback_data="rasm:oddiy")],
            [_ikb("💎 Maxsus Rasm", callback_data="rasm:maxsus")],
        ]
    )


def oddiy_rasm_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[_ikb("⬅️ Bekor qilish", callback_data="rasm:back")]])


def oddiy_rasm_styles_keyboard() -> InlineKeyboardMarkup:
    from data.rasm_uslublari_data import STYLES

    rows = []
    row = []
    for style in STYLES:
        row.append(_ikb(f"{style['id']}-rasm", callback_data=f"oddiyrasm:{style['id']}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([_ikb("⬅️ Orqaga", callback_data="rasm:back")])
    return InlineKeyboardMarkup(rows)


def oddiy_rasm_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("🔁 Yana rasm yasash", callback_data="rasm:oddiy")]]
    )


# ---------- 🎬 Video Yasash ----------

def video_insufficient_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("💳 Hisobni to'ldirish", callback_data="topup:paid")]]
    )


def video_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[_ikb("⬅️ Bekor qilish", callback_data="video:cancel")]])


# ============================================================================
# 🎵 Musiqa yaratish (bosh menyu tugmasi)
# ============================================================================

# key -> (tugma matni/emoji, admin uchun chiroyli nom)
MUSIC_GENRES = {
    "jazz": ("🎷 Jazz musiqa", "🎷 Jazz"),
    "bass": ("🎸 Bass musiqa", "🎸 Bass"),
    "calm": ("🌙 Sokin musiqa", "🌙 Sokin"),
    "rap": ("🔥 Rep musiqa", "🔥 Rep"),
}

MUSIC_LANGS = {
    "uz": ("🇺🇿 O'zbek tili", "🇺🇿 O'zbekcha"),
    "ru": ("🇷🇺 Rus tili", "🇷🇺 Ruscha"),
    "ar": ("🇸🇦 Arab tili", "🇸🇦 Arabcha"),
    "en": ("🇬🇧 Ingliz tili", "🇬🇧 Inglizcha"),
}


def music_genre_keyboard() -> InlineKeyboardMarkup:
    items = list(MUSIC_GENRES.items())
    rows = []
    for i in range(0, len(items), 2):
        pair = items[i:i + 2]
        rows.append(
            [_ikb(label, style="primary", callback_data=f"music:genre:{key}") for key, (label, _) in pair]
        )
    rows.append([_ikb("🔙 Orqaga", callback_data="music:cancel")])
    return InlineKeyboardMarkup(rows)


def music_language_keyboard(genre: str) -> InlineKeyboardMarkup:
    rows = [
        [_ikb(label, style="primary", callback_data=f"music:lang:{genre}:{key}")]
        for key, (label, _) in MUSIC_LANGS.items()
    ]
    rows.append([_ikb("🔙 Orqaga", callback_data="music:back_genre")])
    return InlineKeyboardMarkup(rows)


def music_prepare_keyboard(genre: str, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🎧 Musiqa tayyorlash", style="primary", callback_data=f"music:prepare:{genre}:{lang}")],
            [_ikb("🔙 Orqaga", callback_data=f"music:back_lang:{genre}")],
        ]
    )


def music_admin_send_keyboard(user_id: int, genre: str, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("🎵 Musiqani yuborish", style="primary", callback_data=f"musicsend:{user_id}:{genre}:{lang}")]]
    )


def music_limit_reached_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("👑 Pro obuna sotib olish", style="primary", callback_data="prosub:buy")]]
    )


# ============================================================================
# 🛒 Free Fire Do'koni (bosh menyu tugmasi)
# ============================================================================

def store_menu_keyboard() -> InlineKeyboardMarkup:
    from data.store_data import STORE_ITEMS

    rows = [
        [_ikb(item["label"], callback_data=f"storeitem:{item['key']}")]
        for item in STORE_ITEMS
    ]
    return InlineKeyboardMarkup(rows)


def store_item_detail_keyboard(key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🛒 Sotib olish", callback_data=f"storebuy:{key}")],
            [_ikb("⬅️ Orqaga", callback_data="store:back")],
        ]
    )


def store_admin_review_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("✅ Yubordim", callback_data=f"store_sent:{order_id}")]]
    )


# ============================================================================
# 🎁 Giftlar (bosh menyu tugmasi - o'yin ichidagi gift buyurtmalari)
# ============================================================================

def gift_order_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("🎁 Character Gift", callback_data="giftorder:character")],
            [_ikb("🎁 Emote Gift", callback_data="giftorder:emote")],
            [_ikb("🎁 Gun Skin Gift", callback_data="giftorder:gunskin")],
            [_ikb("🎁 Evo Gun Gift", callback_data="giftorder:evogun")],
            [_ikb("🎁 Bundle Gift", callback_data="giftorder:bundle")],
        ]
    )


def gift_order_item_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Orqaga", callback_data="giftorder:back")]]
    )


def gift_order_admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("💬 Narx aytish", callback_data=f"giftreply:{user_id}")]]
    )


# ============================================================================
# 🏆 Yutiqni chiqarish (bosh menyu tugmasi - Pul yoki Almaz)
# ============================================================================

def withdraw_win_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _ikb("💵 Pul chiqarish", callback_data="winwd:cash"),
                _ikb("💎 Almaz chiqarish", callback_data="winwd:diamond"),
            ]
        ]
    )


def withdraw_win_cash_not_enough_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("❌ Yechib bo'lmaydi", callback_data="winwd:noop")],
            [_ikb("⬅️ Orqaga", callback_data="winwd:back")],
        ]
    )


# ============================================================================
# 🆘 AVTOMATIK: yuqoridagi BARCHA "*_keyboard" funksiyalari (InlineKeyboardMarkup
# qaytaradiganlari) shu yerda avtomatik "o'raladi" - har biri chaqirilganda
# natijaviy klaviatura _with_ff_menu_and_help() orqali o'tkaziladi. Shu
# sababli yangi funksiya qo'shilganda ham (agar u "_keyboard" bilan tugasa
# va InlineKeyboardMarkup qaytarsa) qo'lda hech narsa qilish shart emas -
# "🎮 Free Fire menyu" va qizil "🎧 Yordam" tugmalari o'zi qo'shiladi.
# ============================================================================

# start_inline_keyboard() - bu allaqachon "🎮 Free Fire menyu" tugmasi
# bosilganda ko'rsatiladigan YANGI asosiy (bosh) menyuning o'zi (⚙️
# Nastroykalar, ✨ Nik yaratish, 📰 News, 👤 Hisobim). Shu sabab unga яна
# bir marta "🎮 Free Fire menyu" tugmasini qo'shish shart emas (o'zini
# o'ziga qaytaradigan ortiqcha tugma bo'lib qolardi) - faqat qizil
# "🎧 Yordam" tugmasi qo'shiladi.
# subscription_keyboard() - majburiy obuna ekrani. Foydalanuvchi hali
# kanallarga obuna bo'lmagan bo'lishi mumkin, shu sabab bu yerda
# "🎮 Free Fire menyu" tugmasi ko'rsatilmaydi ("✅ Obuna bo'ldim"
# tugmasi tagida ortiqcha/chalg'ituvchi bo'lib qolardi).
_SKIP_NAV_BUTTON_FUNCS = {"start_inline_keyboard", "subscription_keyboard"}


def _wrap_inline_keyboard_func(func):
    skip_nav = func.__name__ in _SKIP_NAV_BUTTON_FUNCS

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        return _with_ff_menu_and_help(func(*args, **kwargs), skip_nav=skip_nav)
    return _wrapper


def _auto_wrap_all_inline_keyboards():
    module = inspect.getmodule(_auto_wrap_all_inline_keyboards)
    module_globals = vars(module)
    for name, obj in list(module_globals.items()):
        if not name.endswith("_keyboard"):
            continue
        if not inspect.isfunction(obj):
            continue
        if getattr(obj, "_ff_menu_help_wrapped", False):
            continue
        try:
            ret_annotation = inspect.signature(obj).return_annotation
        except (TypeError, ValueError):
            continue
        if ret_annotation is not InlineKeyboardMarkup:
            continue
        wrapped = _wrap_inline_keyboard_func(obj)
        wrapped._ff_menu_help_wrapped = True
        module_globals[name] = wrapped


_auto_wrap_all_inline_keyboards()
