# -*- coding: utf-8 -*-
"""🏆 Yutiqni chiqarish - foydalanuvchi pul yoki almaz ko'rinishida yutug'ini
yechib olishi mumkin.

- 💎 Almaz tanlansa: mavjud 💎 Almaz yechish oqimi qayta ishlatiladi (kamida
  450 dona almaz talab qilinadi).
- 💵 Pul tanlansa: hisobidan so'm yechiladi (bir martada maksimum 20 000
  so'm, kamida 20 000 so'm balans talab qilinadi), so'rov adminga boradi.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    withdraw_win_type_keyboard,
    withdraw_win_cash_not_enough_keyboard,
)

WAITING_WITHDRAW_CASH_AMOUNT = 93

MAX_CASH_WITHDRAW = 20000
MIN_BALANCE_FOR_CASH_WITHDRAW = 20000

WIN_TEXT = "🏆 <b>Yutiqni chiqarish</b>\n\nNimani chiqarmoqchisiz? 👇"


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def on_withdraw_win_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WIN_TEXT, parse_mode="HTML", reply_markup=withdraw_win_type_keyboard()
    )


async def on_withdraw_win_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        WIN_TEXT, parse_mode="HTML", reply_markup=withdraw_win_type_keyboard()
    )
    return ConversationHandler.END


async def on_withdraw_win_cash_noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(
        f"Yechish uchun kamida {MIN_BALANCE_FOR_CASH_WITHDRAW:,} so'm balans kerak.".replace(",", "."),
        show_alert=True,
    )


async def on_withdraw_win_cash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    balance = db.get_balance(user_id)

    if balance < MIN_BALANCE_FOR_CASH_WITHDRAW:
        await query.edit_message_text(
            "💵 <b>Pul chiqarish</b>\n\n"
            f"Yechish uchun hisobingizda kamida <b>{MIN_BALANCE_FOR_CASH_WITHDRAW:,} so'm</b> "
            "bo'lishi kerak.\n\n"
            f"Sizda hozircha: <b>{balance:,} so'm</b>.".replace(",", "."),
            parse_mode="HTML",
            reply_markup=withdraw_win_cash_not_enough_keyboard(),
        )
        return ConversationHandler.END

    await query.edit_message_text(
        "💵 <b>Pul chiqarish</b>\n\n"
        f"Necha so'm yechmoqchisiz? (bir martada maksimum {MAX_CASH_WITHDRAW:,} so'm)\n\n"
        "Faqat raqam yuboring. Bekor qilish uchun /bekor.".replace(",", "."),
        parse_mode="HTML",
    )
    return WAITING_WITHDRAW_CASH_AMOUNT


async def receive_withdraw_cash_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    raw = (update.message.text or "").strip().replace(" ", "")

    if not raw.isdigit():
        await update.message.reply_text("⚠️ Noto'g'ri format. Faqat raqam kiriting.")
        return WAITING_WITHDRAW_CASH_AMOUNT

    amount = int(raw)
    user_id = update.effective_user.id

    if amount <= 0:
        await update.message.reply_text("⚠️ Miqdor 0 dan katta bo'lishi kerak.")
        return WAITING_WITHDRAW_CASH_AMOUNT

    if amount > MAX_CASH_WITHDRAW:
        await update.message.reply_text(
            f"⚠️ Bir martada maksimum {MAX_CASH_WITHDRAW:,} so'm yechish mumkin.".replace(",", ".")
        )
        return WAITING_WITHDRAW_CASH_AMOUNT

    balance = db.get_balance(user_id)
    if not db.deduct_balance(user_id, amount):
        await update.message.reply_text(
            f"❌ Hisobingizda mablag' yetarli emas. Joriy balans: {balance:,} so'm.".replace(",", "."),
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END

    user = update.effective_user
    db.create_cash_withdraw_request(user_id, amount)

    await update.message.reply_text(
        "✅ <b>So'rovingiz qabul qilindi!</b>\n\n"
        f"💵 <b>{amount:,} so'm</b> tez orada sizga o'tkaziladi.".replace(",", "."),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "💵 <b>Yangi pul yechish so'rovi (Yutiqni chiqarish)</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"💵 Miqdor: <b>{amount:,} so'm</b>".replace(",", ".")
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")
    except TelegramError:
        pass

    return ConversationHandler.END


async def cancel_withdraw_cash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END
