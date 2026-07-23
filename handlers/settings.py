# -*- coding: utf-8 -*-
"""⚙️ Nastroykalar bo'limi - brend va model tanlash callback'lari."""

from telegram import Update
from telegram.ext import ContextTypes

from keyboards import brands_keyboard, models_keyboard, model_back_keyboard
from data.settings_data import format_settings_text, PHONES


async def on_brand_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    brand = query.data.split(":", 1)[1]
    if brand not in PHONES:
        return
    await query.edit_message_text(
        f"{brand}\n\nModelni tanlang 👇",
        reply_markup=models_keyboard(brand),
    )


async def on_back_to_brands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📱⚙️ Telefon uchun nastroyka\n\nTelefon brendini tanlang 👇",
        reply_markup=brands_keyboard(),
    )


async def on_model_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    model_name = query.data.split(":", 1)[1]
    text = format_settings_text(model_name)

    # Modelning tegishli brendini topamiz (orqaga tugmasi uchun)
    brand = None
    for b, models in PHONES.items():
        if any(m[0] == model_name for m in models):
            brand = b
            break

    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=model_back_keyboard(brand) if brand else None,
    )
