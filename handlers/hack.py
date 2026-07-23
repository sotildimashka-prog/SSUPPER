# -*- coding: utf-8 -*-
"""💣 Free Fire Hack - Proxy server, Cheat va panellar, Mening FF ID'im
bittasi ostida jamlangan bo'lim (inline tugmalar, har birida orqaga tugmasi)."""

from telegram import Update
from telegram.ext import ContextTypes

from keyboards import hack_menu_keyboard, hack_back_keyboard
from handlers.content import send_stored_content

DEFAULT_CHEAT_TEXT = "🔧 <b>Cheat va panellar</b>\n\nTez orada qo'shiladi."
DEFAULT_PROXY_TEXT = "🌐 <b>Proxy server</b>\n\nHozircha bo'sh."

HACK_MENU_TEXT = "🔫🔥 <b>Maxsus xizmat</b>\n\nKerakli bo'limni tanlang 👇"


async def on_hack_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HACK_MENU_TEXT, parse_mode="HTML", reply_markup=hack_menu_keyboard()
    )


async def on_hack_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_stored_content(
        query.message, "proxy_text", DEFAULT_PROXY_TEXT, reply_markup=hack_back_keyboard()
    )


async def on_hack_cheat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_stored_content(
        query.message, "cheat_text", DEFAULT_CHEAT_TEXT, reply_markup=hack_back_keyboard()
    )


async def on_hack_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_text(
            HACK_MENU_TEXT, parse_mode="HTML", reply_markup=hack_menu_keyboard()
        )
    except Exception:
        await query.message.reply_text(
            HACK_MENU_TEXT, parse_mode="HTML", reply_markup=hack_menu_keyboard()
        )
