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
from data.guides_data import GUIDES

# ---------- Asosiy menyu (ReplyKeyboard) ----------

BTN_HELP = "💬 Yordam"
BTN_SETTINGS = "🎯 Nastroykalar"
BTN_NICKS = "🏷️ Niklar"
BTN_GUIDES = "📖 Qo'llanmalar"
BTN_PREMIUM = "👑 Premium bo'lim"
BTN_CHEAT = "🛠️ Cheat va panellar"
BTN_FFID = "🕹️ Mening FF ID'im"
BTN_PROXY = "🛰️ Proxy server"
BTN_STATS = "📈 Statistika"
BTN_BROADCAST = "📣 Xabar yuborish"
BTN_POST = "🖋️ Post"


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(BTN_HELP), KeyboardButton(BTN_SETTINGS)],
        [KeyboardButton(BTN_NICKS), KeyboardButton(BTN_GUIDES)],
        [KeyboardButton(BTN_PREMIUM), KeyboardButton(BTN_CHEAT)],
        [KeyboardButton(BTN_FFID), KeyboardButton(BTN_PROXY)],
    ]
    if is_admin:
        rows.append([KeyboardButton(BTN_STATS), KeyboardButton(BTN_BROADCAST)])
        rows.append([KeyboardButton(BTN_POST)])
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


# ---------- Nastroykalar (brendlar -> modellar) ----------

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
            [
                InlineKeyboardButton(m[0], callback_data=f"model:{m[0]}")
                for m in chunk
            ]
        )
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_brands")])
    return InlineKeyboardMarkup(rows)


def model_back_keyboard(brand: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Modellarga qaytish", callback_data=f"brand:{brand}")]]
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
