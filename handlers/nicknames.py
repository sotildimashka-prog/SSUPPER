# -*- coding: utf-8 -*-
"""🆔 Niklar bo'limi callback'lari."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from data.nicknames_data import MALE_NICKNAMES, FEMALE_NICKNAMES


def _format_list(title: str, nicks: list) -> str:
    # HTML <code> formatida - foydalanuvchi ustiga bosib nusxa oladi
    lines = [f"<code>{n}</code>" for n in nicks]
    return f"{title}\n\n" + "\n".join(lines)


def _back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_nicks")]]
    )


async def on_nick_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.split(":", 1)[1]

    if category == "male":
        text = _format_list("👦 <b>Erkaklar niklari</b>", MALE_NICKNAMES)
    else:
        text = _format_list("👧 <b>Qizlar niklari</b>", FEMALE_NICKNAMES)

    await query.edit_message_text(
        text, parse_mode="HTML", reply_markup=_back_keyboard()
    )


async def on_back_to_nicks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from keyboards import nicknames_keyboard

    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🆔 Niklar\n\nKategoriyani tanlang 👇",
        reply_markup=nicknames_keyboard(),
    )
