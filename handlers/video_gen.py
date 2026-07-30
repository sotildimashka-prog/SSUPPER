# -*- coding: utf-8 -*-
"""🎬 Video Yasash bo'limi.

Faqat hisobida kamida VIDEO_MIN_BALANCE (30 000 so'm) bo'lgan foydalanuvchilar
video buyurtma berishi mumkin. Yetarli mablag' bo'lmasa, hisobni to'ldirish
haqida xabar chiqadi (mavjud "Hisobim to'ldirish" oqimi qayta ishlatiladi).

Yetarli mablag' bo'lsa: foydalanuvchi video uchun prompt/matn yozadi -> summa
hisobidan yechiladi -> buyurtma adminga yuboriladi (admin tayyor videoni
yuboradi, mavjud "customreply:" oqimi orqali).
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    video_insufficient_keyboard,
    video_cancel_keyboard,
    custom_admin_keyboard,
    VIDEO_MIN_BALANCE,
)
from handlers.subscription import require_subscription

WAITING_VIDEO_PROMPT = range(1)[0]


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def _fmt(amount: int) -> str:
    return f"{amount:,}".replace(",", " ")


async def on_video_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_subscription(update, context):
        return ConversationHandler.END
    user = update.effective_user
    balance = db.get_balance(user.id)

    if balance < VIDEO_MIN_BALANCE:
        await update.message.reply_text(
            "🎬 <b>Video Yasash</b>\n\n"
            "⛔️ Bu bo'lim faqat pullik foydalanuvchilar uchun ishlaydi.\n\n"
            f"💰 Sizning hisobingiz: <b>{_fmt(balance)} so'm</b>\n"
            f"📌 Video yaratish uchun kamida <b>{_fmt(VIDEO_MIN_BALANCE)} so'm</b> kerak.\n\n"
            "Hisobingizni to'ldirish uchun pastdagi tugmani bosing 👇",
            parse_mode="HTML",
            reply_markup=video_insufficient_keyboard(),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "🎬 <b>Video Yasash</b>\n\n"
        f"💰 Hisobingiz: <b>{_fmt(balance)} so'm</b>\n\n"
        "✍️ Video uchun nima xohlayotganingizni (mavzu/g'oya) batafsil yozing.\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
        reply_markup=video_cancel_keyboard(),
    )
    return WAITING_VIDEO_PROMPT


async def on_video_cancel_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    is_admin = _is_admin(query.from_user.id)
    try:
        await query.message.delete()
    except TelegramError:
        pass
    await query.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END


async def cancel_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END


async def receive_video_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    prompt_text = (update.message.text or "").strip()
    if not prompt_text:
        await update.message.reply_text("⚠️ Iltimos, matn ko'rinishida yozing.")
        return WAITING_VIDEO_PROMPT

    balance = db.get_balance(user.id)
    if balance < VIDEO_MIN_BALANCE:
        is_admin = _is_admin(user.id)
        await update.message.reply_text(
            "⛔️ Hisobingizda mablag' yetarli emas. Avval hisobingizni to'ldiring.",
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END

    ok = db.deduct_balance(user.id, VIDEO_MIN_BALANCE)
    is_admin = _is_admin(user.id)
    if not ok:
        await update.message.reply_text(
            "⛔️ Hisobingizda mablag' yetarli emas. Avval hisobingizni to'ldiring.",
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END
    new_balance = db.get_balance(user.id)

    await update.message.reply_text(
        "✅ Buyurtmangiz qabul qilindi!\n\n"
        f"💳 Hisobingizdan <b>{_fmt(VIDEO_MIN_BALANCE)} so'm</b> yechildi.\n"
        f"💰 Qolgan balans: <b>{_fmt(new_balance)} so'm</b>\n\n"
        "🎬 Admin tez orada videongizni tayyorlab yuboradi.",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "🎬 <b>Yangi VIDEO YASASH buyurtmasi!</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"💰 To'langan: {_fmt(VIDEO_MIN_BALANCE)} so'm\n\n"
        f"📝 So'rov:\n{prompt_text}"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=custom_admin_keyboard(user.id),
        )
    except TelegramError:
        pass

    return ConversationHandler.END
