# -*- coding: utf-8 -*-
"""🎮 Nik yaratish - foydalanuvchi ism yuboradi, bot shu ismga avtomatik
100 ta chiroyli Free Fire nik yaratadi."""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from keyboards import nick_creation_back_keyboard
from data.nicknames_data import generate_custom_nicknames

WAITING_NICK_NAME = 70

# 🆕 Yangi (faqat inline tugmali) oqimda pastki (Reply) "Asosiy menyu"
# klaviaturasi endi HECH QAERDA ko'rsatilmaydi - shu sabab bu yerda ham
# eski main_menu_keyboard() o'rniga oddiy inline "⬅️ Bosh menyu" tugmasi
# ishlatiladi (bosilganda /start xabariga qaytaradi).
_BACK_TO_START_KB = InlineKeyboardMarkup(
    [[InlineKeyboardButton("⬅️ Bosh menyu", callback_data="start:back")]]
)

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
            reply_markup=_BACK_TO_START_KB if is_last else None,
        )
    return ConversationHandler.END


async def cancel_nick_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=_BACK_TO_START_KB
    )
    return ConversationHandler.END
