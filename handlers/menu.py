# -*- coding: utf-8 -*-
"""/haqida, /menu, /profil, /yordam, /yangiliklar buyruqlari va oddiy tugma javoblari."""

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from config import ADMIN_ID, BOT_NAME, HELP_CONTACT, PREMIUM_CONTACT, NEWS_CHANNEL_URL
from keyboards import (
    main_menu_keyboard,
    brands_keyboard,
    nicknames_keyboard,
    guides_keyboard,
)

ABOUT_TEXT = (
    f"ℹ️ <b>{BOT_NAME} haqida</b>\n\n"
    "Ushbu bot Free Fire o'yinchilariga eng maqbul sensitivity nastroykalarini, "
    "premium nicknamelarni, foydali qo'llanmalarni va o'yin statistikasini "
    "topishda yordam beradi.\n\n"
    "🛠 Doimiy yangilanib boriladi va yangi imkoniyatlar qo'shiladi."
)

DEFAULT_HELP_TEXT = (
    "🆘 <b>Yordam</b>\n\n"
    "Agar botdan foydalanishda biror muammoga duch kelsangiz yoki savolingiz "
    f"bo'lsa, quyidagi manzilga murojaat qiling:\n\n👤 {HELP_CONTACT}"
)

DEFAULT_PREMIUM_TEXT = (
    "🔥 <b>Premium xizmatlar</b>\n\n"
    "✅ VIP nastroykalar\n"
    "✅ Premium HUD\n"
    "✅ Maxsus DPI\n"
    "✅ Premium support\n"
    "✅ Yangilanishlar\n\n"
    "💰 <b>Narxlar:</b>\n"
    "🥉 Bronze — 15 000 so'm\n"
    "🥈 Silver — 30 000 so'm\n"
    "🥇 Gold — 50 000 so'm\n\n"
    f"👤 Bog'lanish uchun: {PREMIUM_CONTACT}"
)

DEFAULT_CHEAT_TEXT = "🔧 <b>Cheat va panellar</b>\n\nTez orada qo'shiladi."
DEFAULT_PROXY_TEXT = "🌐 <b>Proxy server</b>\n\nHozircha bo'sh."


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def haqida_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ABOUT_TEXT, parse_mode="HTML")


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text(
        "🏠 <b>Bosh menyu</b>\n\nKerakli bo'limni tanlang 👇",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )


async def profil_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    row = db.get_user(user.id)
    joined = row["joined_at"][:10] if row else "—"
    balance = db.get_balance(user.id)
    text = (
        "🆔 <b>Profil ma'lumotlari</b>\n\n"
        f"👤 Ism: {user.first_name or '-'}\n"
        f"🔗 Username: @{user.username if user.username else '—'}\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"📅 Ro'yxatdan o'tgan sana: {joined}\n"
        f"💰 Balans: {balance:,} so'm".replace(",", ".")
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def yordam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = db.get_setting("help_text", DEFAULT_HELP_TEXT)
    await update.message.reply_text(text, parse_mode="HTML")


async def yangiliklar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📢 Yangiliklar kanalimizga o'tish uchun bosing:\n{NEWS_CHANNEL_URL}"
    )


# ---------- ReplyKeyboard tugma bosilganda ishlaydigan handlerlar ----------

async def on_help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = db.get_setting("help_text", DEFAULT_HELP_TEXT)
    await update.message.reply_text(text, parse_mode="HTML")


async def on_premium_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = db.get_setting("premium_text", DEFAULT_PREMIUM_TEXT)
    await update.message.reply_text(text, parse_mode="HTML")


async def on_cheat_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = db.get_setting("cheat_text", DEFAULT_CHEAT_TEXT)
    await update.message.reply_text(text, parse_mode="HTML")


async def on_proxy_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = db.get_setting("proxy_text", DEFAULT_PROXY_TEXT)
    await update.message.reply_text(text, parse_mode="HTML")


async def on_settings_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 <b>Nastroykalar</b>\n\nTelefon brendini tanlang 👇",
        parse_mode="HTML",
        reply_markup=brands_keyboard(),
    )


async def on_nicks_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏷️ <b>Niklar</b>\n\nKategoriyani tanlang 👇",
        parse_mode="HTML",
        reply_markup=nicknames_keyboard(),
    )


async def on_guides_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>Qo'llanmalar</b>\n\nMavzuni tanlang 👇",
        parse_mode="HTML",
        reply_markup=guides_keyboard(),
    )
