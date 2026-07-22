# -*- coding: utf-8 -*-
"""Reply va Inline klaviaturalarni yaratish."""

from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import REQUIRED_CHANNELS, ADMIN_ID
from data.settings_data import PHONES
from data.tablet_data import TABLETS
from data.guides_data import GUIDES
from data.diamonds_data import PACKAGES, SUBSCRIPTIONS, button_label

# ---------- Asosiy menyu (ReplyKeyboard) ----------

BTN_SETTINGS = "🎯 Nastroykalar"
BTN_NICKS = "🏷️ Niklar"
BTN_TABLET = "📲 Planshet nastroykalari"
BTN_CHEAT = "🛠️ Cheat va panellar"
BTN_FFID = "🕹️ Mening FF ID'im"
BTN_PROXY = "🛰️ Proxy server"
BTN_DIAMONDS = "💎 Almaz sotib olish"
BTN_ACCOUNT = "💰 Hisobim"
BTN_HELP = "💬 Yordam"
BTN_GUIDES = "📖 Qo'llanmalar"
BTN_PREMIUM = "👑 Premium bo'lim"
BTN_STATS = "📈 Statistika"
BTN_BROADCAST = "📣 Xabar yuborish"
BTN_POST = "🖋️ Post"
BTN_EDIT_TEXTS = "✏️ Tugmalarni tahrirlash"


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(BTN_SETTINGS), KeyboardButton(BTN_NICKS)],
        [KeyboardButton(BTN_TABLET), KeyboardButton(BTN_CHEAT)],
        [KeyboardButton(BTN_FFID), KeyboardButton(BTN_PROXY)],
        [KeyboardButton(BTN_DIAMONDS), KeyboardButton(BTN_ACCOUNT)],
        [KeyboardButton(BTN_HELP), KeyboardButton(BTN_GUIDES)],
        [KeyboardButton(BTN_PREMIUM)],
    ]
    if is_admin:
        rows.append([KeyboardButton(BTN_STATS), KeyboardButton(BTN_BROADCAST)])
        rows.append([KeyboardButton(BTN_POST), KeyboardButton(BTN_EDIT_TEXTS)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


# ---------- Majburiy obuna ----------

def subscription_keyboard() -> InlineKeyboardMarkup:
    rows = []
    channels = REQUIRED_CHANNELS
    for i in range(0, len(channels), 2):
        chunk = channels[i:i + 2]
        rows.append(
            [
                InlineKeyboardButton(f"📡 {ch['name']}", url=f"https://t.me/{ch['username']}")
                for ch in chunk
            ]
        )
    rows.append([InlineKeyboardButton("✅ Obuna bo'ldim", callback_data="check_sub")])
    return InlineKeyboardMarkup(rows)


# ---------- Pro/Bot o'yinchi savoli va guruhga qo'shish ----------

def player_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏆 Pro o'yinchiman", callback_data="player:pro"),
                InlineKeyboardButton("🤖 Bot o'yinchiman", callback_data="player:bot"),
            ]
        ]
    )


def add_to_group_keyboard(bot_username: str) -> InlineKeyboardMarkup:
    url = f"https://t.me/{bot_username}?startgroup=true"
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("➕ Botni guruhga qo'shish", url=url)]]
    )


# ---------- Nastroykalar (telefon: brendlar -> modellar) ----------

def brands_keyboard() -> InlineKeyboardMarkup:
    rows = []
    brands = list(PHONES.keys())
    for i in range(0, len(brands), 2):
        chunk = brands[i:i + 2]
        rows.append(
            [InlineKeyboardButton(b, callback_data=f"brand:{b}") for b in chunk]
        )
    return InlineKeyboardMarkup(rows)


def models_keyboard(brand: str) -> InlineKeyboardMarkup:
    rows = []
    models = PHONES.get(brand, [])
    for i in range(0, len(models), 2):
        chunk = models[i:i + 2]
        rows.append(
            [InlineKeyboardButton(m[0], callback_data=f"model:{m[0]}") for m in chunk]
        )
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_brands")])
    return InlineKeyboardMarkup(rows)


def model_back_keyboard(brand: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Modellarga qaytish", callback_data=f"brand:{brand}")]]
    )


# ---------- Planshet nastroykalari ----------

def tablet_brands_keyboard() -> InlineKeyboardMarkup:
    rows = []
    brands = list(TABLETS.keys())
    for i in range(0, len(brands), 2):
        chunk = brands[i:i + 2]
        rows.append(
            [InlineKeyboardButton(b, callback_data=f"tbrand:{b}") for b in chunk]
        )
    return InlineKeyboardMarkup(rows)


def tablet_models_keyboard(brand: str) -> InlineKeyboardMarkup:
    rows = []
    models = TABLETS.get(brand, [])
    for i in range(0, len(models), 2):
        chunk = models[i:i + 2]
        rows.append(
            [InlineKeyboardButton(m[0], callback_data=f"tmodel:{m[0]}") for m in chunk]
        )
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_tbrands")])
    return InlineKeyboardMarkup(rows)


def tablet_model_back_keyboard(brand: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Modellarga qaytish", callback_data=f"tbrand:{brand}")]]
    )


# ---------- Niklar ----------

def nicknames_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👦 Erkaklar niklari", callback_data="nick:male"),
                InlineKeyboardButton("👧 Qizlar niklari", callback_data="nick:female"),
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
            [InlineKeyboardButton(v["title"], callback_data=f"guide:{k}") for k, v in chunk]
        )
    return InlineKeyboardMarkup(rows)


def guide_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Qo'llanmalarga qaytish", callback_data="back_to_guides")]]
    )


# ---------- Almaz sotib olish ----------

def diamonds_entry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👤 Admin orqali olish", callback_data="dia:admin"),
                InlineKeyboardButton("🤖 Bot orqali olish", callback_data="dia:bot"),
            ]
        ]
    )


def diamonds_admin_keyboard(admin_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"https://t.me/{admin_username}")]]
    )


def diamonds_packages_keyboard() -> InlineKeyboardMarkup:
    rows = []
    items = [{**p, "type": "package"} for p in PACKAGES]
    for i in range(0, len(items), 2):
        chunk = items[i:i + 2]
        rows.append(
            [InlineKeyboardButton(button_label(it), callback_data=f"pkg:{it['key']}") for it in chunk]
        )
    sub_items = [{**s, "type": "subscription"} for s in SUBSCRIPTIONS]
    for i in range(0, len(sub_items), 2):
        chunk = sub_items[i:i + 2]
        rows.append(
            [InlineKeyboardButton(button_label(it), callback_data=f"pkg:{it['key']}") for it in chunk]
        )
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="dia:back")])
    return InlineKeyboardMarkup(rows)


def package_detail_keyboard(key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🛒 Sotib olish", callback_data=f"buy:{key}")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="dia:bot")],
        ]
    )


def insufficient_balance_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("💰 Hisobim", callback_data="go_account")]]
    )


# ---------- Hisobim ----------

def account_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👤 Admin orqali to'ldirish", callback_data="acc:admin"),
                InlineKeyboardButton("💳 Humo/Uzcard orqali to'ldirish", callback_data="acc:card"),
            ]
        ]
    )


def account_admin_keyboard(admin_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"https://t.me/{admin_username}")]]
    )


def paid_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ To'lov qildim", callback_data="topup:paid")]]
    )


def admin_topup_review_keyboard(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Ha", callback_data=f"topup_ok:{request_id}"),
                InlineKeyboardButton("❌ Yo'q", callback_data=f"topup_no:{request_id}"),
            ]
        ]
    )


def admin_order_review_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ Yubordim", callback_data=f"order_sent:{order_id}")]]
    )


# ---------- Admin: matnlarni tahrirlash ----------

def edit_texts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💬 Yordam matni", callback_data="edittext:help_text"),
                InlineKeyboardButton("👑 Premium matni", callback_data="edittext:premium_text"),
            ],
            [
                InlineKeyboardButton("🛠️ Cheat matni", callback_data="edittext:cheat_text"),
                InlineKeyboardButton("🛰️ Proxy matni", callback_data="edittext:proxy_text"),
            ],
        ]
    )
