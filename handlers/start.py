# -*- coding: utf-8 -*-
"""/start buyrug'i va majburiy obuna tekshiruvi."""

from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID, BOT_NAME
from keyboards import subscription_keyboard, main_menu_keyboard
from handlers.subscription import get_unsubscribed_channels

WELCOME_TEXT = (
    "👋 <b>Assalomu aleykum!</b>\n\n"
    f"{BOT_NAME} botiga xush kelibsiz!\n\n"
    "Botdan to'liq foydalanish uchun quyidagi kanallarga obuna bo'ling, "
    "so'ngra <b>✅ Obuna bo'ldim</b> tugmasini bosing 👇"
)

ALREADY_SUBSCRIBED_TEXT = (
    "✅ <b>Obuna tasdiqlandi!</b>\n\n"
    "Endi botning barcha imkoniyatlaridan foydalanishingiz mumkin. "
    "Quyidagi menyudan kerakli bo'limni tanlang 👇"
)


async def notify_admin_new_user(context: ContextTypes.DEFAULT_TYPE, user):
    text = (
        "🆕 <b>Yangi foydalanuvchi</b>\n\n"
        f"👤 Ism: {user.first_name or '-'}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🔗 Username: @{user.username if user.username else '—'}\n"
        f"🕒 Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="HTML")
    except TelegramError:
        pass


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = db.add_user_if_new(user.id, user.first_name or "", user.username or "")

    if is_new:
        await notify_admin_new_user(context, user)

    unsubscribed = await get_unsubscribed_channels(user.id, context)
    if unsubscribed:
        await update.message.reply_text(
            WELCOME_TEXT,
            parse_mode="HTML",
            reply_markup=subscription_keyboard(),
        )
        return

    is_admin = user.id == ADMIN_ID
    await update.message.reply_text(
        ALREADY_SUBSCRIBED_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    unsubscribed = await get_unsubscribed_channels(user.id, context)
    if unsubscribed:
        names = "\n".join(f"• {ch['name']}" for ch in unsubscribed)
        await query.answer(
            "❌ Siz hali barcha kanallarga obuna bo'lmagansiz!", show_alert=True
        )
        return

    is_admin = user.id == ADMIN_ID
    await query.message.delete()
    await context.bot.send_message(
        chat_id=user.id,
        text=ALREADY_SUBSCRIBED_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )
