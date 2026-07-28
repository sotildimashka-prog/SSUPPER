# -*- coding: utf-8 -*-
"""🛠️ Xizmatlar (bosh menyu bo'limi) - Bonuslar, To'lov qilish, FAQ, Qo'llanmalar,
Yangiliklar va boshqa xizmatlar shu yerga yig'ilgan."""

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from config import NEWS_CHANNEL_URL, MUSIC_URL
from keyboards import (
    services_menu_keyboard,
    services_bonus_keyboard,
    services_other_keyboard,
    back_to_services_keyboard,
    back_to_services_other_keyboard,
    website_service_keyboard,
    music_service_keyboard,
    guides_keyboard,
    custom_entry_keyboard,
    hack_menu_keyboard,
    paid_confirm_keyboard,
)
from config import CARD_NUMBER, CARD_HOLDER_NAME, CARD_PHONE

SERVICES_MENU_TEXT = "🛠️ <b>Xizmatlar</b>\n\nKerakli bo'limni tanlang 👇"
SERVICES_OTHER_TEXT = "🔧 <b>Boshqa xizmatlar</b>\n\nKerakli bo'limni tanlang 👇"

DEFAULT_HELP_TEXT = (
    "🆘 <b>Yordam</b>\n\n"
    "Agar botdan foydalanishda biror muammoga duch kelsangiz yoki savolingiz "
    "bo'lsa, quyidagi manzilga murojaat qiling."
)
DEFAULT_FF2017_TEXT = (
    "🎬 <b>Free Fire 2017</b>\n\nHozircha kontent qo'shilmagan. Tez orada bo'ladi!"
)


# ---------- Asosiy Xizmatlar menyusi ----------

async def on_services_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        SERVICES_MENU_TEXT, parse_mode="HTML", reply_markup=services_menu_keyboard()
    )


async def on_back_to_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        SERVICES_MENU_TEXT, parse_mode="HTML", reply_markup=services_menu_keyboard()
    )


# ---------- 🎁 Bonuslar ----------

async def on_svc_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎁 <b>Bonuslar</b>\n\nKerakli bo'limni tanlang 👇",
        parse_mode="HTML",
        reply_markup=services_bonus_keyboard(),
    )


# ---------- 💳 To'lov qilish (hisobni to'ldirish) ----------

async def on_svc_pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "Assalomu aleykum, to'lov uchun karta raqami ⚡️\n\n"
        f"( Isim familiya {CARD_HOLDER_NAME} ) ⚡️ boshqa isim chiqsa to'lov qilmang\n\n"
        "cheksiz qabul yo'q, ulangan raqam: "
        f"{CARD_PHONE}\n\n"
        f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        "(ustiga bosangiz nusxa olinadi) 🎉\n\n"
        "To'lov qilib bo'lgach, pastdagi <b>✅ To'lov qildim</b> tugmasini bosing."
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=paid_confirm_keyboard())


# ---------- 📚 Qo'llanmalar ----------

async def on_svc_guides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📚 <b>Qo'llanmalar</b>\n\nMavzuni tanlang 👇",
        parse_mode="HTML",
        reply_markup=guides_keyboard(),
    )


# ---------- 📰 Yangiliklar ----------

async def on_svc_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"📰 Eng so'nggi Free Fire yangiliklarini kanalimizdan kuzatib boring 👇\n{NEWS_CHANNEL_URL}",
        reply_markup=website_service_keyboard(),
    )


# ---------- 🔧 Boshqa xizmatlar ----------

async def on_svc_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        SERVICES_OTHER_TEXT, parse_mode="HTML", reply_markup=services_other_keyboard()
    )


async def on_back_to_services_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        SERVICES_OTHER_TEXT, parse_mode="HTML", reply_markup=services_other_keyboard()
    )


async def _send_stored_content_inline(query, key: str, default_text: str, back_markup):
    """Matn yoki media (rasm/video/fayl) saqlangan kontentni inline bo'limda ko'rsatadi."""
    content = db.get_content(key, default_text)
    ctype = content.get("type", "text")
    caption = content.get("caption") or content.get("text") or default_text

    if ctype == "text" or not content.get("file_id"):
        await query.edit_message_text(caption, parse_mode="HTML", reply_markup=back_markup)
        return

    chat_id = query.message.chat_id
    bot = query.get_bot()
    try:
        await query.edit_message_text("⏳ Yuklanmoqda...")
    except Exception:
        pass

    if ctype == "photo":
        await bot.send_photo(chat_id, content["file_id"], caption=caption, parse_mode="HTML", reply_markup=back_markup)
    elif ctype == "video":
        await bot.send_video(chat_id, content["file_id"], caption=caption, parse_mode="HTML", reply_markup=back_markup)
    elif ctype == "document":
        await bot.send_document(chat_id, content["file_id"], caption=caption, parse_mode="HTML", reply_markup=back_markup)
    else:
        await bot.send_message(chat_id, caption, parse_mode="HTML", reply_markup=back_markup)


async def on_svcother_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _send_stored_content_inline(
        query, "help_text", DEFAULT_HELP_TEXT, back_to_services_other_keyboard()
    )


async def on_svcother_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🏆 Turnirlar va musobaqalar haqida to'liq ma'lumot uchun saytimizga o'ting 👇",
        reply_markup=website_service_keyboard(),
    )


async def on_svcother_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎵 Free Fire qo'shig'ini tinglash uchun bosing 👇",
        reply_markup=music_service_keyboard(MUSIC_URL),
    )


async def on_svcother_hack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔓 <b>Free Fire Hack</b>\n\nKerakli bo'limni tanlang 👇",
        parse_mode="HTML",
        reply_markup=hack_menu_keyboard(),
    )


async def on_svcother_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "⚠️ <b>Shaxsiy nastroyka</b>\n\nQuyidagilardan birini tanlang 👇",
        parse_mode="HTML",
        reply_markup=custom_entry_keyboard(),
    )


async def on_svcother_ff2017(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _send_stored_content_inline(
        query, "ff2017_content", DEFAULT_FF2017_TEXT, back_to_services_other_keyboard()
    )
