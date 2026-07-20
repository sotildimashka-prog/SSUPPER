# -*- coding: utf-8 -*-
"""📚 Qo'llanmalar bo'limi callback'lari."""

from telegram import Update
from telegram.ext import ContextTypes

from data.guides_data import GUIDES
from keyboards import guides_keyboard, guide_back_keyboard


async def on_guide_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    guide = GUIDES.get(key)
    if not guide:
        return
    await query.edit_message_text(
        guide["text"], parse_mode="HTML", reply_markup=guide_back_keyboard()
    )


async def on_back_to_guides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📚 Qo'llanmalar\n\nMavzuni tanlang 👇",
        reply_markup=guides_keyboard(),
    )
