# -*- coding: utf-8 -*-
"""📊 Statistika va 📢 Xabar yuborish - faqat admin uchun."""

import asyncio

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import main_menu_keyboard

WAITING_BROADCAST = 2


def _admin_only(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID


async def on_stats_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return
    stats = db.get_stats()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"📅 Bugungi yangi foydalanuvchilar: <b>{stats['today_users']}</b>\n"
        f"📈 Bugungi /start bosishlar: <b>{stats['today_starts']}</b>\n"
        f"📨 Jami xabarlar soni: <b>{stats['total_messages']}</b>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END
    await update.message.reply_text(
        "📢 Barcha foydalanuvchilarga yuboriladigan xabar matnini kiriting.\n"
        "Bekor qilish uchun /bekor.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return WAITING_BROADCAST


async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END

    message = update.message
    user_ids = db.get_all_user_ids()

    await update.message.reply_text(
        f"⏳ Xabar {len(user_ids)} foydalanuvchiga yuborilmoqda..."
    )

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await context.bot.copy_message(
                chat_id=uid,
                from_chat_id=message.chat_id,
                message_id=message.message_id,
            )
            sent += 1
        except TelegramError:
            failed += 1
        await asyncio.sleep(0.05)  # Telegram flood limitidan qochish uchun

    await update.message.reply_text(
        f"✅ Xabar yuborildi!\n\n📨 Muvaffaqiyatli: {sent}\n❌ Xatolik: {failed}",
        reply_markup=main_menu_keyboard(True),
    )
    return ConversationHandler.END
