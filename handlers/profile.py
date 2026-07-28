# -*- coding: utf-8 -*-
"""👤 Profil (bosh menyu bo'limi) - profil ma'lumotlari, hisobim va almaz yechish
shu yerga jamlangan."""

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from keyboards import profile_keyboard, account_keyboard


def _profile_text(update: Update) -> str:
    user = update.effective_user
    row = db.get_user(user.id)
    joined = row["joined_at"][:10] if row else "—"
    balance = db.get_balance(user.id)
    return (
        "🆔 <b>Profil ma'lumotlari</b>\n\n"
        f"👤 Ism: {user.first_name or '-'}\n"
        f"🔗 Username: @{user.username if user.username else '—'}\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"📅 Ro'yxatdan o'tgan sana: {joined}\n"
        f"💰 Balans: {balance:,} so'm".replace(",", ".")
    )


async def on_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        _profile_text(update), parse_mode="HTML", reply_markup=profile_keyboard()
    )


def _account_text(user_id: int) -> str:
    balance = db.get_balance(user_id)
    return (
        f"💰 <b>Hisobim</b>\n\n"
        f"💵 Joriy balans: <b>{balance:,} so'm</b>\n\n".replace(",", ".")
        + "Hisobingizni qanday to'ldirmoqchisiz?"
    )


async def on_profile_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        _account_text(query.from_user.id),
        parse_mode="HTML",
        reply_markup=account_keyboard(),
    )
