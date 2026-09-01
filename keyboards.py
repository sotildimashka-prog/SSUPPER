# -*- coding: utf-8 -*-
"""Reply va Inline klaviaturalarni yaratish."""

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from config import (
    REQUIRED_CHANNELS,
    ADMIN_ID,
    WEBSITE_URL,
    WEBAPP_URL,
    NEWS_CHANNEL_URL,
    ORDERS_CHANNEL_ID,
)
from data.settings_data import PHONES
from data.tablet_data import TABLETS
from data.pc_data import PC_MODELS
from data.guides_data import GUIDES
from data.diamonds_data import PACKAGES, SUBSCRIPTIONS, button_label


import re

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
BTN_MY_ACCOUNT = "👛 Hisobim"

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


VIDEO_MIN_BALANCE = 30000

ORDERS_CHANNEL_USERNAME = ORDERS_CHANNEL_ID.lstrip("@")

# Har safar pastki (Reply) tugmalar tarkibi yoki rangi o'zgarganda bu
# raqamni +1 oshiring. Shunda barcha foydalanuvchilarning eski (keshlangan)
# tugmalar oynasi ular botga keyingi safar yozganda YOKI istalgan tugmani
# (reply yoki inline) bosganda AVTOMATIK yangilanadi — broadcast yuborish
# shart emas.
MENU_VERSION = 10


def full_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Barcha xizmatlar ochilgan TO'LIQ pastki menyu (eski asosiy menyu).
    "🛠️ Barcha xizmatlar" inline tugmasi bosilganda shu klaviatura
    yuboriladi - hech qanday handler o'zgarmagani uchun barcha eski
    tugmalar oldingidek to'liq ishlayveradi."""
    buttons: list[tuple[str, dict]] = [
        (BTN_PORTAL, {"web_app": WebAppInfo(url=WEBAPP_URL)}),
        (BTN_M2_SERVICES, {}),
        (BTN_M2_SETTINGS, {}),
        (BTN_M2_NICKS, {}),
        (BTN_MAIN_RASM, {}),
        (BTN_MAIN_VIDEO, {}),
        (BTN_MAIN_MUSIC, {}),
        (BTN_STORE, {}),
        (BTN_MY_ACCOUNT, {}),
        (BTN_M2_PAYMENTS, {}),
        (BTN_MINI_GAMES, {}),
        (BTN_GIFTS, {}),
        (BTN_PRO_SUB, {}),
        (BTN_WITHDRAW_WIN, {}),
        (BTN_ORDERS_CHANNEL, {}),
        (BTN_GIFT_ORDER, {}),
        (BTN_M2_FAQ, {}),
        (BTN_M2_DIAMONDS, {}),
    ]

    if is_admin:
        buttons.extend(
            [
                (BTN_STATS, {}),
                (BTN_BROADCAST, {}),
                (BTN_POST, {}),
                (BTN_EDIT_TEXTS, {}),
                (BTN_ADMIN_CREDIT, {}),
                (BTN_GIFT_ALL, {}),
                (BTN_DEDUCT_DIAMOND, {}),
            ]
        )

    rows = []
    for i in range(0, len(buttons), 2):
        chunk = buttons[i:i + 2]
        rows.append([_kb(text, **kwargs) for text, kwargs in chunk])

    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


# ---------- 🆕 /start xabari (rasm + 3 ta inline tugma) ----------

NEWS_CHANNEL_USERNAME = "xonfirestream"

START_ACCOUNT_CB = "start:account"
START_SERVICES_CB = "start:services"


def start_inline_keyboard() -> InlineKeyboardMarkup:
    """/start bosilganda rasm ostiga chiqadigan 3 ta inline tugma:
    tepada 🛠️ Barcha xizmatlar (yagona, kattaroq), pastda 👛 Hisobim va
    📰 Yangiliklar (ikkitasi yonma-yon)."""
    return InlineKeyboardMarkup(
        [
            [_ikb("🛠️ Barcha xizmatlar", callback_data=START_SERVICES_CB)],
            [
                _ikb(BTN_MY_ACCOUNT, callback_data=START_ACCOUNT_CB),
                _ikb("📰 Yangiliklar", url=f"https://t.me/{NEWS_CHANNEL_USERNAME}"),
            ],
        ]
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
_ALL_SERVICES_ITEMS = [
    (BTN_M2_SERVICES, f"{SVC_ALL_PREFIX}:services"),
    (BTN_M2_SETTINGS, f"{SVC_ALL_PREFIX}:settings"),
    (BTN_M2_NICKS, f"{SVC_ALL_PREFIX}:nicks"),
    # (BTN_MAIN_RASM, f"{SVC_ALL_PREFIX}:rasm"),
    # (BTN_MAIN_VIDEO, f"{SVC_ALL_PREFIX}:video"),
    # (BTN_MAIN_MUSIC, f"{SVC_ALL_PREFIX}:music"),
    # (BTN_STORE, f"{SVC_ALL_PREFIX}:store"),
    (BTN_M2_PAYMENTS, f"{SVC_ALL_PREFIX}:payments"),
    (BTN_MINI_GAMES, f"{SVC_ALL_PREFIX}:games"),
    (BTN_GIFTS, f"{SVC_ALL_PREFIX}:gifts"),
    (BTN_PRO_SUB, f"{SVC_ALL_PREFIX}:prosub"),
    (BTN_WITHDRAW_WIN, f"{SVC_ALL_PREFIX}:withdrawwin"),
    (BTN_ORDERS_CHANNEL, f"{SVC_ALL_PREFIX}:orders"),
    # (BTN_GIFT_ORDER, f"{SVC_ALL_PREFIX}:giftorder"),
    (BTN_M2_DIAMONDS, f"{SVC_ALL_PREFIX}:diamonds"),
]


def all_services_inline_keyboard() -> InlineKeyboardMarkup:
    rows = [[_ikb(BTN_PORTAL, web_app=WebAppInfo(url=WEBAPP_URL))]]

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


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    # Barcha tugmalar (matn, qo'shimcha kwarg) tartibida - keyin 2 tadan
    # qatorlarga bo'linadi. Tartib chiroyli juftlashishi uchun махсус
    # tanlangan (funksiyalarning o'zi o'zgarmaydi, faqat joylashuvi):
    #   🗺 Free Fire Portal | 🛍 Xizmatlar
    #   ⚙️ Nastroykalar      | 🎉 Free Fire Niklar
    #   🖼️ Rasm Yasash       | 🎬 Video Yasash
    #   🎵 Musiqa yaratish   | 🛒 Free Fire Do'koni
    #   👛 Hisobim           | 💰 To'lov usullari
    #   🎮 Mini O'yinlar     | 🎁 Sovg'alar
    #   👑 Pro obuna         | 🏆 Yutiqni chiqarish
    #   📢 Buyurtmalar       | 🎁 Giftlar
    #   📬 Savollar (FAQ)    | 💎 Almaz olish
    # MUHIM: Foydalanuvchi so'rovi bo'yicha asosiy menyudagi barcha
    # tugmalar vaqtincha o'chirilgan - faqat "👛 Hisobim" tugmasi qoladi.
    # Boshqa tugmalarning kodlari (BTN_PORTAL, BTN_M2_SERVICES va h.k.)
    # va ularga tegishli handlerlar/ma'lumotlar hech qanday o'chirilmadi -
    # ular shunchaki quyidagi ro'yxatdan olib tashlandi. Kerak bo'lsa,
    # pastdagi qatorlarni qayta izohdan chiqarib qaytarish mumkin.
    buttons: list[tuple[str, dict]] = [
        # MUHIM: Foydalanuvchi so'rovi bo'yicha "👛 Hisobim" pastki (reply)
        # tugmasi ham olib tashlandi - endi asosiy pastki menyuda (admin
        # bo'lmagan foydalanuvchilar uchun) hech qanday tugma qolmaydi.
        # Kodning o'zi (BTN_MY_ACCOUNT va h.k.) o'chirilmagan - kerak
        # bo'lsa pastdagi qatorni qayta izohdan chiqarib qaytarish mumkin.
        # (BTN_MY_ACCOUNT, {}),
        # (BTN_PORTAL, {"web_app": WebAppInfo(url=WEBAPP_URL)}),
        # (BTN_M2_SERVICES, {}),
        # (BTN_M2_SETTINGS, {}),
        # (BTN_M2_NICKS, {}),
        # (BTN_MAIN_RASM, {}),
        # (BTN_MAIN_VIDEO, {}),
        # (BTN_MAIN_MUSIC, {}),
        # (BTN_STORE, {}),
        # (BTN_M2_PAYMENTS, {}),
        # (BTN_MINI_GAMES, {}),
        # (BTN_GIFTS, {}),
        # (BTN_PRO_SUB, {}),
        # (BTN_WITHDRAW_WIN, {}),
        # (BTN_ORDERS_CHANNEL, {}),
        # (BTN_GIFT_ORDER, {}),
        # (BTN_M2_FAQ, {}),
        # (BTN_M2_DIAMONDS, {}),
    ]

    if is_admin:
        buttons.extend(
            [
                (BTN_STATS, {}),
                (BTN_BROADCAST, {}),
                (BTN_POST, {}),
                (BTN_EDIT_TEXTS, {}),
                (BTN_ADMIN_CREDIT, {}),
                (BTN_GIFT_ALL, {}),
                (BTN_DEDUCT_DIAMOND, {}),
            ]
        )

    # 2 tadan qilib qatorlarga bo'lish (funksiyalarga tegilmaydi, faqat
    # joylashuv o'zgaradi).
    rows = []
    for i in range(0, len(buttons), 2):
        chunk = buttons[i:i + 2]
        rows.append([_kb(text, **kwargs) for text, kwargs in chunk])

    # MUHIM: Foydalanuvchi so'rovi bo'yicha - agar chiqadigan pastki (reply)
    # tugma umuman bo'lmasa (admin bo'lmagan foydalanuvchilar uchun), bo'sh
    # ReplyKeyboardMarkup o'rniga ReplyKeyboardRemove qaytariladi - shunda
    # ekranda "bo'sh"/qulaysiz klaviatura paneli ko'rinmaydi, u butunlay
    # OLIB TASHLANADI (hech qanday tugma qolmaydi).
    if not rows:
        return ReplyKeyboardRemove()

    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


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
    rows = []
    channels = REQUIRED_CHANNELS
    for i in range(0, len(channels), 2):
        chunk = channels[i:i + 2]
        rows.append(
            [
                _ikb(f"📡 {ch['name']}", url=f"https://t.me/{ch['username']}")
                for ch in chunk
            ]
        )
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
    rows.append([_ikb("⬅️ Free Fire menyu", callback_data="back_to_ff")])
    return InlineKeyboardMarkup(rows)


def models_keyboard(brand: str) -> InlineKeyboardMarkup:
    rows = []
    models = PHONES.get(brand, [])
    for i in range(0, len(models), 2):
        chunk = models[i:i + 2]
        rows.append(
            [_ikb(m[0], callback_data=f"model:{m[0]}") for m in chunk]
        )
    rows.append([_ikb("⬅️ Orqaga", callback_data="back_to_brands")])
    return InlineKeyboardMarkup(rows)


def model_back_keyboard(brand: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Modellarga qaytish", callback_data=f"brand:{brand}")]]
    )


# ---------- Planshet nastroykalari ----------

def tablet_brands_keyboard() -> InlineKeyboardMarkup:
    rows = []
    brands = list(TABLETS.keys())
    for i in range(0, len(brands), 2):
        chunk = brands[i:i + 2]
        rows.append(
            [_ikb(b, callback_data=f"tbrand:{b}") for b in chunk]
        )
    rows.append([_ikb("⬅️ Free Fire menyu", callback_data="back_to_ff")])
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
        ]
    )


def account_admin_keyboard(admin_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [_ikb("💬 Admin bilan bog'lanish", url=f"https://t.me/{admin_username}")],
            [_ikb("⬅️ Orqaga", callback_data="acc:back")],
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
            ]
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


# ---------- 💎 Almaz yechish ----------

def withdraw_amount_keyboard(amount: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb(f"💎 {amount}", callback_data=f"withdraw_confirm:{amount}")]]
    )


# ---------- 💎 Almaz yechish (🆕 yangi oqim: avval "Hisobim", pastida "Yechish") ----------

def withdraw_account_keyboard() -> InlineKeyboardMarkup:
    """"Hisobim" (joriy almaz balansi) matni ostida chiqadigan yagona
    "💎 Yechish" inline tugmasi."""
    return InlineKeyboardMarkup(
        [[_ikb("💎 Yechish", callback_data="withdraw:start")]]
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
        [[_ikb("⬅️ Free Fire menyu", callback_data="back_to_ff")]]
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
    rows.append([_ikb("⬅️ Free Fire menyu", callback_data="back_to_ff")])
    return InlineKeyboardMarkup(rows)


def pc_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ PC modellariga qaytish", callback_data="back_to_pc")]]
    )


# ---------- 🎮 Nik yaratish (orqaga) ----------

def nick_creation_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Free Fire menyu", callback_data="back_to_ff")]]
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
        ]
    )


def new_nicks_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("⬅️ Orqaga", callback_data="newnick:back")]]
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
    return InlineKeyboardMarkup(
        [[_ikb("💰 To'lov usullari", callback_data="myacc:pay")]]
    )


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
