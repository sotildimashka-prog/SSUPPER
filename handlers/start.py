# -*- coding: utf-8 -*-
"""/start buyrug'i, majburiy obuna tekshiruvi va pro/bot o'yinchi savoli."""

from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID, BOT_NAME
from keyboards import (
    subscription_keyboard,
    main_menu_keyboard,
    player_type_keyboard,
    add_to_group_keyboard,
)
from handlers.subscription import get_unsubscribed_channels

def first_greeting_text(first_name: str) -> str:
    name = first_name or ""
    return (
        f"Assalomu aleykum {name} 👋\n\n"
        "📋 O'zingizga kerakli tugmani bosish orqali menuni chiqarishingiz mumkin.\n\n"
        "🤖 Men free fire o'yini uchun mukammal hizmat ko'rsatadigan botman.\n\n"
        "❓ Savollaringiz bormi? Hammasi joyida! \"Savol va Takliflar❓\" tugmasini "
        "bosing va biz imkon qadar tezroq javob berishga harakat qilamiz."
    )

SUBSCRIBE_TEXT = (
    "Botdan to'liq foydalanish uchun avval quyidagi kanallarga obuna bo'ling, "
    "so'ngra pastdagi <b>✅ Obuna bo'ldim</b> tugmasini bosing 👇"
)

WELCOME_BACK_TEXT = (
    "🎉 <b>Ajoyib! Obuna tasdiqlandi!</b>\n\n"
    f"✨ {BOT_NAME} ga xush kelibsiz, endi botning barcha imkoniyatlaridan "
    "to'liq foydalanishingiz mumkin! 🔥"
)

PLAYER_TYPE_QUESTION = "🎮 <b>Siz PRO o'yinchimisiz yoki BOT o'yinchimisiz?</b> 👇"

ADD_TO_GROUP_TEXT = (
    "➕ <b>Botni guruhingizga qo'shing!</b>\n\n"
    "Do'stlaringiz bilan birga Free Fire nastroykalari va yangiliklaridan "
    "bahramand bo'ling. Pastdagi tugmani bosing 👇"
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


async def _send_player_type_question(update_or_query, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    await context.bot.send_message(
        chat_id=chat_id,
        text=PLAYER_TYPE_QUESTION,
        parse_mode="HTML",
        reply_markup=player_type_keyboard(),
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = db.add_user_if_new(user.id, user.first_name or "", user.username or "")

    if is_new:
        await notify_admin_new_user(context, user)

    # 1) Birinchi salomlashuv
    await update.message.reply_text(
        first_greeting_text(user.first_name), parse_mode="HTML"
    )

    # 2) Majburiy obuna tekshiruvi
    unsubscribed = await get_unsubscribed_channels(user.id, context)
    if unsubscribed:
        await update.message.reply_text(
            SUBSCRIBE_TEXT,
            parse_mode="HTML",
            reply_markup=subscription_keyboard(),
        )
        return

    # Agar allaqachon obuna bo'lgan bo'lsa - to'g'ridan-to'g'ri asosiy menyuga
    is_admin = user.id == ADMIN_ID
    await update.message.reply_text(WELCOME_BACK_TEXT, parse_mode="HTML")
    await _send_player_type_question(update, context, update.effective_chat.id)
    await update.message.reply_text(
        "👇 Asosiy menyu tayyor:",
        reply_markup=main_menu_keyboard(is_admin),
    )


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    unsubscribed = await get_unsubscribed_channels(user.id, context)
    if unsubscribed:
        await query.answer(
            "❌ Siz hali barcha kanallarga obuna bo'lmagansiz!", show_alert=True
        )
        return

    is_admin = user.id == ADMIN_ID
    try:
        await query.message.delete()
    except TelegramError:
        pass

    # 3) Obuna tasdiqlangandan keyingi ikkinchi salomlashuv
    await context.bot.send_message(
        chat_id=user.id, text=WELCOME_BACK_TEXT, parse_mode="HTML"
    )
    # 4) Pro/Bot o'yinchi savoli
    await _send_player_type_question(query, context, user.id)
    # 5) Asosiy menyu
    await context.bot.send_message(
        chat_id=user.id,
        text="👇 Asosiy menyu tayyor:",
        reply_markup=main_menu_keyboard(is_admin),
    )


async def on_player_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pro yoki Bot o'yinchi tanlanganda - ikkalasida ham guruhga qo'shish taklifi chiqadi."""
    query = update.callback_query
    await query.answer()

    me = await context.bot.get_me()
    try:
        await query.edit_message_text(
            ADD_TO_GROUP_TEXT,
            parse_mode="HTML",
            reply_markup=add_to_group_keyboard(me.username),
        )
    except TelegramError:
        pass
