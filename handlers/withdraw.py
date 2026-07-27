# -*- coding: utf-8 -*-
"""💎 Almaz yechish - foydalanuvchi 'Tekin almaz'dan yig'gan almazlarini yechib olish
uchun Free Fire ID yozadi, so'rov adminga boradi."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import main_menu_keyboard

WAITING_WITHDRAW_FF_ID = 40


async def on_withdraw_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    amount = db.get_quiz_diamonds(user_id)

    if amount <= 0:
        await update.message.reply_text(
            "💎 <b>Almaz yechish</b>\n\n"
            "Hozircha yig'ilgan almazingiz yo'q. Avval 💎 <b>Tekin almaz</b> "
            "bo'limidan savollarga javob berib, almaz to'plang.",
            parse_mode="HTML",
        )
        return ConversationHandler.END

    context.user_data["withdraw_amount"] = amount
    await update.message.reply_text(
        f"💎 <b>Almaz yechish</b>\n\n"
        f"Sizda yig'ilgan: <b>{amount}</b> dona almaz bor.\n\n"
        "Ularni yechib olish uchun Free Fire UID (ID) raqamingizni yuboring:\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_WITHDRAW_FF_ID


async def receive_withdraw_ff_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ff_id = (update.message.text or "").strip()
    is_admin = update.effective_user.id == ADMIN_ID

    if not ff_id.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Faqat raqamlardan iborat Free Fire UID yuboring."
        )
        return WAITING_WITHDRAW_FF_ID

    user = update.effective_user
    amount = context.user_data.get("withdraw_amount", 0)

    # Almazlarni "yechilgan" deb hisoblab, hisobdan ayiramiz
    db.reset_quiz_diamonds(user.id)

    await update.message.reply_text(
        "✅ <b>So'rovingiz qabul qilindi!</b>\n\n"
        f"💎 <b>{amount}</b> dona almaz tez orada Free Fire hisobingizga o'tkaziladi.",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "💎 <b>Yangi almaz yechish so'rovi (Tekin almaz)</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"🎮 Free Fire UID: <code>{ff_id}</code>\n"
        f"💎 Miqdor: <b>{amount}</b> dona almaz"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")
    except TelegramError:
        pass

    context.user_data.pop("withdraw_amount", None)
    return ConversationHandler.END


async def cancel_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id == ADMIN_ID
    context.user_data.pop("withdraw_amount", None)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END
