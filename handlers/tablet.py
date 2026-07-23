# -*- coding: utf-8 -*-
"""📲 Planshet nastroykalari bo'limi - brend va model tanlash callback'lari."""

from telegram import Update
from telegram.ext import ContextTypes

from keyboards import tablet_brands_keyboard, tablet_models_keyboard, tablet_model_back_keyboard
from data.tablet_data import format_tablet_settings_text, TABLETS


async def on_tablet_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📲✨ <b>Planshet nastroyka</b>\n\nPlanshet brendini tanlang 👇",
        parse_mode="HTML",
        reply_markup=tablet_brands_keyboard(),
    )


async def on_tablet_brand_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    brand = query.data.split(":", 1)[1]
    if brand not in TABLETS:
        return
    await query.edit_message_text(
        f"{brand}\n\nModelni tanlang 👇",
        reply_markup=tablet_models_keyboard(brand),
    )


async def on_back_to_tablet_brands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📲✨ Planshet nastroyka\n\nPlanshet brendini tanlang 👇",
        reply_markup=tablet_brands_keyboard(),
    )


async def on_tablet_model_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    model_name = query.data.split(":", 1)[1]
    text = format_tablet_settings_text(model_name)

    brand = None
    for b, models in TABLETS.items():
        if any(m[0] == model_name for m in models):
            brand = b
            break

    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=tablet_model_back_keyboard(brand) if brand else None,
    )
