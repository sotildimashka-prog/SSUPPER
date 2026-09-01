# -*- coding: utf-8 -*-
"""🎮 Free Fire (bosh menyu bo'limi) - Telefon/Planshet/PC nastroyka va Nik yaratish."""

from telegram import Update
from telegram.ext import ContextTypes

from handlers.message_utils import safe_edit_message

from keyboards import ff_menu_keyboard, brands_keyboard, tablet_brands_keyboard, pc_keyboard

FF_MENU_TEXT = "🎮 <b>Free Fire</b>\n\nKerakli bo'limni tanlang 👇"


async def on_ff_main_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        FF_MENU_TEXT, parse_mode="HTML", reply_markup=ff_menu_keyboard()
    )


async def on_back_to_ff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit_message(query,
        FF_MENU_TEXT, parse_mode="HTML", reply_markup=ff_menu_keyboard()
    )


async def on_ff_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit_message(query,
        "📱⚙️ <b>Telefon nastroyka</b>\n\nTelefon brendini tanlang 👇",
        parse_mode="HTML",
        reply_markup=brands_keyboard(),
    )


async def on_ff_tablet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit_message(query,
        "📲✨ <b>Planshet nastroyka</b>\n\nPlanshet brendini tanlang 👇",
        parse_mode="HTML",
        reply_markup=tablet_brands_keyboard(),
    )


async def on_ff_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit_message(query,
        "💻✨ <b>PC nastroyka</b>\n\nKompyuter konfiguratsiyasini tanlang 👇",
        parse_mode="HTML",
        reply_markup=pc_keyboard(),
    )
