# -*- coding: utf-8 -*-
"""🎮 Nik yaratish - foydalanuvchi ism yuboradi, bot shu ismga 20+ ta chiroyli
Free Fire nik yaratadi."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID
from keyboards import main_menu_keyboard, nick_creation_back_keyboard
from data.nicknames_data import generate_custom_nicknames

WAITING_NICK_NAME = 70

ASK_NAME_TEXT = (
    "🎮 <b>Nik yaratish</b>\n\n"
    "Ismingizni (yoki istalgan so'zni) yuboring, men shu asosda 20+ ta "
    "chiroyli Free Fire nik yarataman.\n\n"
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
    text = (
        f"🎮 <b>\"{name}\"</b> uchun nikneymlar tayyor!\n\n" + "\n".join(lines) +
        "\n\n👆 Ustiga bosib nusxa olishingiz mumkin."
    )
    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END


async def cancel_nick_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id == ADMIN_ID
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END
