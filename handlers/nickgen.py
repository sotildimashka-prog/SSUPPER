# -*- coding: utf-8 -*-
"""🎮 Nik yaratish - foydalanuvchi ism yuboradi, bot shu ismga avtomatik
100 ta chiroyli Free Fire nik yaratadi."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID
from keyboards import main_menu_keyboard, nick_creation_back_keyboard
from data.nicknames_data import generate_custom_nicknames

WAITING_NICK_NAME = 70

ASK_NAME_TEXT = (
    "🎮 <b>Nik yaratish</b>\n\n"
    "Ismingizni (yoki istalgan so'zni, hatto g'ayrioddiy ismlarni ham) yuboring, "
    "men shu asosda avtomatik <b>100 ta</b> chiroyli Free Fire nik yarataman.\n\n"
    "Bekor qilish uchun /bekor yozing."
)


async def start_nick_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        ASK_NAME_TEXT, parse_mode="HTML", reply_markup=nick_creation_back_keyboard()
    )
    return WAITING_NICK_NAME


async def receive_nick_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = (update.message.text or "").strip()
    is_admin = update.effective_user.id == ADMIN_ID

    if not name:
        await update.message.reply_text("⚠️ Iltimos, ism yoki so'z yuboring.")
        return WAITING_NICK_NAME

    nicks = generate_custom_nicknames(name)
    lines = [f"<code>{n}</code>" for n in nicks]

    header = f"🎮 <b>\"{name}\"</b> uchun {len(nicks)} ta nikneym tayyor!\n\n"
    footer = "\n\n👆 Ustiga bosib nusxa olishingiz mumkin."

    # Telegram xabar chegarasi (4096) dan chiqib ketmasligi uchun, agar juda
    # uzun ism kelsa, natijani bir necha xabarga bo'lib yuboramiz.
    max_len = 3500
    chunks = []
    current = header
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            chunks.append(current)
            current = ""
        current += line + "\n"
    current += footer
    chunks.append(current)

    for i, chunk in enumerate(chunks):
        is_last = i == len(chunks) - 1
        await update.message.reply_text(
            chunk,
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(is_admin) if is_last else None,
        )
    return ConversationHandler.END


async def cancel_nick_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id == ADMIN_ID
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END
