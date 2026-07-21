# -*- coding: utf-8 -*-
"""📊 Statistika, 📢 Xabar yuborish va 📝 Post - faqat admin uchun."""

import asyncio

from telegram import (
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import main_menu_keyboard

WAITING_BROADCAST = 2
WAITING_POST_TEXT = 3
WAITING_POST_BUTTON = 4


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


# ---------- 📢 Oddiy Xabar yuborish (Broadcast) ----------

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
        await asyncio.sleep(0.05)

    await update.message.reply_text(
        f"✅ Xabar yuborildi!\n\n📨 Muvaffaqiyatli: {sent}\n❌ Xatolik: {failed}",
        reply_markup=main_menu_keyboard(True),
    )
    return ConversationHandler.END


# ---------- 📝 Post (tugmali xabar) ----------

async def start_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END
    await update.message.reply_text(
        "📝 <b>Yangi post yaratish</b>\n\n"
        "Post matnini yuboring (rasm bilan ham bo'lishi mumkin, rasmga izoh "
        "sifatida matn yozing).\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    return WAITING_POST_TEXT


async def receive_post_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["post_message"] = update.message

    await update.message.reply_text(
        "🔘 <b>Tugma qo'shasizmi?</b>\n\n"
        "Agar post ostiga bosiladigan tugma qo'shmoqchi bo'lsangiz, quyidagi "
        "formatda yuboring:\n\n"
        "<code>Tugma matni | https://havola.com</code>\n\n"
        "Masalan:\n<code>Kanalga o'tish | https://t.me/kanal_nomi</code>\n\n"
        "Agar tugma kerak bo'lmasa, /otkazib_yuborish deb yozing.\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_POST_BUTTON


async def skip_post_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _broadcast_post(update, context, button=None)


async def receive_post_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()
    if "|" not in raw:
        await update.message.reply_text(
            "⚠️ Format noto'g'ri. Quyidagicha yuboring:\n\n"
            "<code>Tugma matni | https://havola.com</code>\n\n"
            "Yoki tugmasiz davom etish uchun /otkazib_yuborish yozing.",
            parse_mode="HTML",
        )
        return WAITING_POST_BUTTON

    label, url = [p.strip() for p in raw.split("|", 1)]
    if not url.startswith("http"):
        await update.message.reply_text(
            "⚠️ Havola http:// yoki https:// bilan boshlanishi kerak. Qaytadan "
            "urinib ko'ring yoki /otkazib_yuborish yozing."
        )
        return WAITING_POST_BUTTON

    button = InlineKeyboardMarkup([[InlineKeyboardButton(label, url=url)]])
    return await _broadcast_post(update, context, button=button)


async def cancel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("post_message", None)
    await update.message.reply_text(
        "❌ Post yaratish bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def _broadcast_post(update: Update, context: ContextTypes.DEFAULT_TYPE, button):
    original = context.user_data.pop("post_message", None)
    if original is None:
        await update.message.reply_text(
            "⚠️ Xatolik: post matni topilmadi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    user_ids = db.get_all_user_ids()
    await update.message.reply_text(
        f"⏳ Post {len(user_ids)} foydalanuvchiga yuborilmoqda..."
    )

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            if original.photo:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=original.photo[-1].file_id,
                    caption=original.caption or "",
                    parse_mode="HTML",
                    reply_markup=button,
                )
            else:
                await context.bot.send_message(
                    chat_id=uid,
                    text=original.text or "",
                    parse_mode="HTML",
                    reply_markup=button,
                )
            sent += 1
        except TelegramError:
            failed += 1
        await asyncio.sleep(0.05)

    await update.message.reply_text(
        f"✅ Post yuborildi!\n\n📨 Muvaffaqiyatli: {sent}\n❌ Xatolik: {failed}",
        reply_markup=main_menu_keyboard(True),
    )
    return ConversationHandler.END
