# -*- coding: utf-8 -*-
"""💻 PC nastroykalari bo'limi - to'g'ridan-to'g'ri model tanlash callback'lari."""

from telegram import Update
from telegram.ext import ContextTypes

from keyboards import pc_keyboard, pc_back_keyboard
from data.pc_data import format_pc_settings_text


async def on_pc_model_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    model_name = query.data.split(":", 1)[1]
    text = format_pc_settings_text(model_name)
    await query.edit_message_text(
        text, parse_mode="HTML", reply_markup=pc_back_keyboard()
    )


async def on_back_to_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💻✨ <b>PC nastroyka</b>\n\nKompyuter konfiguratsiyasini tanlang 👇",
        parse_mode="HTML",
        reply_markup=pc_keyboard(),
    )
