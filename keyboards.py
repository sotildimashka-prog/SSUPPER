# -*- coding: utf-8 -*-
"""Reply va Inline klaviaturalarni yaratish."""

from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import REQUIRED_CHANNELS, ADMIN_ID, WEBSITE_URL
from data.settings_data import PHONES
from data.tablet_data import TABLETS
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


# Barcha tugmalar uchun standart rang (ko'k) - Bot API 9.4+ talab qiladi.
def _ikb(text, **kwargs):
    display_text = _apply_emoji_icon(text, kwargs)
    return InlineKeyboardButton(display_text, style="primary", **kwargs)


def _kb(text, style="primary", **kwargs):
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


BTN_ADMIN_CREDIT = "🛠 Admin buyrug'i"


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    row_texts = [
        [BTN_WEBSITE],
        [BTN_SETTINGS, BTN_TABLET],
        [BTN_HACK, BTN_CUSTOM],
        [BTN_QUIZ, BTN_DIAMONDS],
        [BTN_NICKS, BTN_NEWS],
        [BTN_MUSIC, BTN_ACCOUNT],
        [BTN_FAQ, BTN_GUIDES],
    ]
    if is_admin:
        row_texts.append([BTN_STATS, BTN_BROADCAST])
        row_texts.append([BTN_POST, BTN_EDIT_TEXTS])
        row_texts.append([BTN_ADMIN_CREDIT])

    # Qatorlar navbat bilan yashil/ko'k rangda, eng oxirgi qator esa qizil bo'ladi.
    rows = []
    last_index = len(row_texts) - 1
    for i, row in enumerate(row_texts):
        if i == last_index:
            row_style = "danger"
        elif i % 2 == 0:
            row_style = "success"
        else:
            row_style = "primary"
        rows.append([_kb(text, style=row_style) for text in row])

    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


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
        [[_ikb("🌐 Saytga o'tish", url=WEBSITE_URL)]]
    )


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
