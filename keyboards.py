# -*- coding: utf-8 -*-
"""Reply va Inline klaviaturalarni yaratish."""

from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from config import REQUIRED_CHANNELS, ADMIN_ID, WEBSITE_URL, WEBAPP_URL, NEWS_CHANNEL_URL
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
    return InlineKeyboardButton(display_text, **kwargs)


# Pastki (Reply) klaviatura tugmalari: barchasi doim YASHIL (success) rangda.
def _kb(text, style="success", **kwargs):
    # MUHIM: ReplyKeyboard tugmasi bosilganda uning matni xabar sifatida
    # botga yuboriladi va bot shu matn orqali tugmani aniqlaydi. Shuning
    # uchun bu yerda emoji olib tashlanmaydi (aks holda tugmalar ishlamay qoladi).
    return KeyboardButton(text, style=style, **kwargs)

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

# ---------- 🖼️ Rasm Yasash / 🎬 Video Yasash (Bosh menyu) ----------

BTN_MAIN_RASM = "🖼️ Rasm Yasash"
BTN_MAIN_VIDEO = "🎬 Video Yasash"

VIDEO_MIN_BALANCE = 30000


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    row_texts = [
        [BTN_M2_DIAMONDS, BTN_M2_SERVICES],
        [BTN_M2_SETTINGS, BTN_M2_NICKS],
        [BTN_M2_PAYMENTS, BTN_M2_FAQ],
        [BTN_MAIN_RASM, BTN_MAIN_VIDEO],
    ]
    if is_admin:
        row_texts.append([BTN_STATS, BTN_BROADCAST])
        row_texts.append([BTN_POST, BTN_EDIT_TEXTS])
        row_texts.append([BTN_ADMIN_CREDIT, BTN_GIFT_ALL])

    # Barcha qatorlar faqat YASHIL (success) rangda.
    rows = [[_kb(text) for text in row] for row in row_texts]

    # 🗺 Free Fire Portal - alohida, birinchi qatorda, to'g'ridan-to'g'ri
    # Web App'ni ochadigan tugma.
    rows.insert(0, [_kb(BTN_PORTAL, web_app=WebAppInfo(url=WEBAPP_URL))])

    # 🎁 Sovg'alar - oddiy matnli tugma (pastda MessageHandler orqali ushlanadi)
    rows.append([_kb(BTN_GIFTS)])

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


def custom_admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[_ikb("📤 Nastroyka yuborish", callback_data=f"customreply:{user_id}")]]
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
        row.append(_ikb(style["title"], callback_data=f"oddiyrasm:{style['id']}"))
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
