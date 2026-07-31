# -*- coding: utf-8 -*-
"""/haqida, /menu, /profil, /yordam, /yangiliklar buyruqlari va oddiy tugma javoblari."""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

import database as db
from config import ADMIN_ID, BOT_NAME, HELP_CONTACT, PREMIUM_CONTACT, NEWS_CHANNEL_URL, MUSIC_URL, WEBSITE_URL
from keyboards import (
    main_menu_keyboard,
    MENU_VERSION,
    brands_keyboard,
    nicknames_keyboard,
    guides_keyboard,
    website_keyboard,
    music_keyboard,
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


async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/update — Telegram'da eski (keshlangan) pastki tugmalar ko'rinishini
    tozalab, botning eng so'nggi menyusini qayta ko'rsatadi. Botga tasodifan
    kirib qolgan foydalanuvchi ham shu buyruq bilan yangilanishlarni darhol
    ko'ra oladi."""
    is_admin = _is_admin(update.effective_user.id)

    # 1) Eski pastki tugmalar oynasini tozalaymiz (mijoz keshini yangilaydi).
    old = await update.message.reply_text(
        "🔄 Yangilanmoqda...", reply_markup=ReplyKeyboardRemove()
    )
    try:
        await old.delete()
    except Exception:
        pass

    # 2) Yangi (eng so'nggi) menyuni ko'rsatamiz.
    await update.message.reply_text(
        "✅ <b>Bot yangilandi!</b>\n\nEng so'nggi menyu tugmalari yuklandi 👇",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )
    db.set_menu_version(update.effective_user.id, MENU_VERSION)


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


async def _send_stored_content(message, key: str, default_text: str):
    content = db.get_content(key, default_text)
    ctype = content.get("type", "text")
    caption = content.get("caption") or content.get("text") or default_text

    if ctype == "text" or not content.get("file_id"):
        await message.reply_text(caption, parse_mode="HTML")
    elif ctype == "photo":
        await message.reply_photo(content["file_id"], caption=caption, parse_mode="HTML")
    elif ctype == "video":
        await message.reply_video(content["file_id"], caption=caption, parse_mode="HTML")
    elif ctype == "document":
        await message.reply_document(content["file_id"], caption=caption, parse_mode="HTML")


async def yordam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_stored_content(update.message, "help_text", DEFAULT_HELP_TEXT)


async def yangiliklar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📢 Yangiliklar kanalimizga o'tish uchun bosing:\n{NEWS_CHANNEL_URL}"
    )


# ---------- ReplyKeyboard tugma bosilganda ishlaydigan handlerlar ----------

async def on_help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_stored_content(update.message, "help_text", DEFAULT_HELP_TEXT)


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


DEFAULT_FF2017_TEXT = (
    "🎬 <b>Free Fire 2017</b>\n\nHozircha kontent qo'shilmagan. Tez orada bo'ladi!"
)


async def on_ff2017_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_stored_content(update.message, "ff2017_content", DEFAULT_FF2017_TEXT)


async def on_website_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏆 Turnirlar va musobaqalar haqida to'liq ma'lumot uchun saytimizga o'ting 👇",
        reply_markup=website_keyboard(),
    )


async def on_news_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📰 Eng so'nggi Free Fire yangiliklarini saytimizdan kuzatib boring 👇",
        reply_markup=website_keyboard(),
    )


async def on_music_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Free Fire qo'shig'ini tinglash uchun bosing 👇",
        reply_markup=music_keyboard(MUSIC_URL),
    )


async def saytimiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🌐 Saytimiz: {WEBSITE_URL}", reply_markup=website_keyboard()
    )
