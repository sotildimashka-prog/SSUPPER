# -*- coding: utf-8 -*-
"""🎮 "Nima gap?" bo'limi (foydalanuvchi tomoni): Free Fire turnirlar va
Free Fire akkauntlar. Admin tomoni handlers/admin.py faylida joylashgan."""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.error import TelegramError

import database as db
from keyboards import (
    nimagap_menu_keyboard,
    fftournament_slots_keyboard,
    TOURNAMENT_SLOT_LABELS,
)
from handlers.start import _edit_in_place

NIMAGAP_TEXT = (
    "🎮 <b>Nima gap, jangchi?!</b> 🔥\n\n"
    "Bu yerda eng so'nggi Free Fire turnirlari va sotuvdagi noyob "
    "akkauntlar haqida bilib olishingiz mumkin. Kerakli bo'limni "
    "tanlang 👇"
)

TOURNAMENTS_MENU_TEXT = (
    "🏆 <b>Free Fire turnirlar</b>\n\n"
    "Qaysi kunga tegishli turnirlarni ko'rmoqchisiz? 👇"
)

ACCOUNTS_TITLE = "🎮 <b>Free Fire akkauntlar</b>\n\n"

_BACK_TO_NIMAGAP_KB = InlineKeyboardMarkup(
    [[InlineKeyboardButton("⬅️ Orqaga", callback_data="nimagap:menu")]]
)


async def on_nimagap_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"🎮 Nima gap?" tugmasi - asosiy /start xabari o'rniga shu menyu
    ko'rsatiladi (tahrirlanadi)."""
    query = update.callback_query
    await query.answer()
    await _edit_in_place(query, NIMAGAP_TEXT, nimagap_menu_keyboard())


TOURNIR_PHOTO_PATH = "assets/turnir_banner.jpg"


async def on_nimagap_tournaments_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"🏆 Free Fire turnirlar" - banner rasm bilan birga 5 ta kun tugmasi
    chiqadi. Asl "Nima gap?" xabari o'zgarmasdan qoladi (tahrirlanmaydi) -
    o'rniga rasmli YANGI xabar yuboriladi."""
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    kb = fftournament_slots_keyboard()
    try:
        with open(TOURNIR_PHOTO_PATH, "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=TOURNAMENTS_MENU_TEXT,
                parse_mode="HTML",
                reply_markup=kb,
            )
    except (FileNotFoundError, TelegramError):
        await context.bot.send_message(
            chat_id=chat_id, text=TOURNAMENTS_MENU_TEXT, parse_mode="HTML", reply_markup=kb
        )


async def on_nimagap_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"🎮 Free Fire akkauntlar" - agar admin qo'shgan bo'lsa rasm/matn +
    "Sotib olish" tugmasi bilan YANGI xabar yuboriladi (asl menyu xabari
    o'zgarmasdan qoladi, shunda foydalanuvchi yana boshqa tugmalarni
    bosishi mumkin)."""
    query = update.callback_query
    await query.answer()

    acc = db.get_ff_account()
    chat_id = query.from_user.id

    if not acc:
        text = (
            ACCOUNTS_TITLE
            + "😔 Hozircha sotuvda akkauntlar yo'q.\n\n"
            "Tez orada eng zo'r akkauntlar bilan qaytamiz, kuzatib boring! 👀"
        )
        try:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        except TelegramError:
            pass
        return

    caption = acc.get("caption") or ""
    text = ACCOUNTS_TITLE + "🔥 <b>Sotuvda yangi akkaunt bor!</b>\n\n" + caption
    buy_url = acc.get("buy_url") or "https://t.me/auwsn"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Sotib olish", url=buy_url)]])

    file_id = acc.get("file_id")
    try:
        if file_id:
            await context.bot.send_photo(
                chat_id=chat_id, photo=file_id, caption=text, parse_mode="HTML", reply_markup=kb
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb
            )
    except TelegramError:
        pass


async def on_fftour_slot_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"fftour:<slot>" - tanlangan kun uchun turnir ma'lumotini YANGI
    xabar sifatida ko'rsatadi (asl kunlar ro'yxati xabari o'zgarmaydi)."""
    query = update.callback_query
    await query.answer()

    slot = query.data.split(":", 1)[1] if query.data and ":" in query.data else ""
    label = TOURNAMENT_SLOT_LABELS.get(slot, "Turnir")
    chat_id = query.from_user.id

    tour = db.get_tournament(slot)
    if not tour:
        text = f"🏆 <b>{label}</b>\n\n😔 Bu kunga turnir qo'shilmagan."
        try:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        except TelegramError:
            pass
        return

    caption = tour.get("caption") or ""
    text = f"🏆 <b>{label}</b>\n\n{caption}"

    channel_url = tour.get("channel_url") or ""
    kb = None
    if channel_url:
        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("📢 Turnir kanaliga o'tish", url=channel_url)]]
        )

    file_id = tour.get("file_id")
    try:
        if file_id:
            await context.bot.send_photo(
                chat_id=chat_id, photo=file_id, caption=text, parse_mode="HTML", reply_markup=kb
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb
            )
    except TelegramError:
        pass
