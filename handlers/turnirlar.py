# -*- coding: utf-8 -*-
"""🏆 Free Fire Turnirlar - asosiy pastki (reply) tugma bosilganda ochiladigan
bo'lim. Admin xohlagancha turnir qo'shishi mumkin (bir kunda 3-4 tasi bo'lsa
ham) - har biri o'z kuni, formati (3/3, 1/1 va h.k.) va vaqti bilan
ko'rsatiladi. Foydalanuvchi ro'yxatdan turnirni tanlaydi yoki "Keyingi
turnir" tugmasi orqali birma-bir ko'rib chiqadi.

Admin tomoni (qo'shish / o'chirish) handlers/admin.py faylida joylashgan -
bu yerda faqat foydalanuvchiga ko'rinadigan qism bor.
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import turnirlar_list_keyboard, turnirlar_detail_keyboard

TURNIR_PHOTO_PATH = "assets/turnir_banner.jpg"

GREETING_TEXT = (
    "🔥 <b>Assalomu alaykum, jasur jangchi!</b> 🔥\n\n"
    "🏆 <b>FREE FIRE TURNIRLAR</b> olamiga xush kelibsiz! ⚔️\n\n"
    "Bu yerda eng qizg'in janglar, katta sovrinlar va shov-shuvli "
    "musobaqalar sizni kutmoqda 🎮💥\n\n"
    "👇 Quyidagi ro'yxatdan turnirni tanlang:"
)

EMPTY_LIST_TEXT = (
    GREETING_TEXT
    + "\n\n😔 Hozircha e'lon qilingan turnir yo'q. Tez orada yangi "
    "turnirlar bilan qaytamiz, kuzatib boring! 👀"
)


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def _list_caption(turnirlar: list) -> str:
    if not turnirlar:
        return EMPTY_LIST_TEXT
    return GREETING_TEXT + f"\n\n📊 Jami turnirlar soni: <b>{len(turnirlar)}</b> ta"


def _detail_caption(turnirlar: list, index: int) -> str:
    total = len(turnirlar)
    t = turnirlar[index]
    day = (t.get("day_label") or "Kun belgilanmagan").strip()
    title = (t.get("title") or "Free Fire Turnir").strip()
    fmt = (t.get("format_text") or "—").strip()
    vaqt = (t.get("time_text") or "").strip()
    note = (t.get("note") or "").strip()

    lines = [
        f"🏆 <b>{title}</b>",
        f"📌 <i>{index + 1}/{total}-turnir</i>\n",
        f"🗓 <b>Kuni:</b> {day}",
        f"⚔️ <b>Format:</b> {fmt}",
    ]
    if vaqt:
        lines.append(f"🕐 <b>Boshlanish vaqti:</b> {vaqt}")
    if note:
        lines.append(f"\n🎁 {note}")
    lines.append("\n🔥 G'alaba sizni kutmoqda, omad! 🍀")
    return "\n".join(lines)


async def _send_photo_screen(chat_id: int, context: ContextTypes.DEFAULT_TYPE, caption: str, reply_markup):
    try:
        with open(TURNIR_PHOTO_PATH, "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
    except (FileNotFoundError, TelegramError):
        await context.bot.send_message(
            chat_id=chat_id, text=caption, parse_mode="HTML", reply_markup=reply_markup
        )


async def _edit_caption(query, context: ContextTypes.DEFAULT_TYPE, caption: str, reply_markup):
    try:
        await query.edit_message_caption(caption=caption, parse_mode="HTML", reply_markup=reply_markup)
    except TelegramError:
        try:
            await query.edit_message_text(text=caption, parse_mode="HTML", reply_markup=reply_markup)
        except TelegramError:
            await context.bot.send_message(
                chat_id=query.from_user.id, text=caption, parse_mode="HTML", reply_markup=reply_markup
            )


async def on_turnirlar_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"🏆 Free Fire Turnirlar" pastki tugmasi bosilganda chaqiriladi."""
    is_admin = _is_admin(update.effective_user.id)
    turnirlar = db.get_turnirlar_list()
    caption = _list_caption(turnirlar)
    kb = turnirlar_list_keyboard(turnirlar, is_admin)
    await _send_photo_screen(update.effective_chat.id, context, caption, kb)


async def on_turnir_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"turnir:open:<id>" - ro'yxatdan tanlangan turnir tafsilotini ko'rsatadi."""
    query = update.callback_query
    await query.answer()
    is_admin = _is_admin(query.from_user.id)

    turnir_id = int(query.data.split(":", 2)[2])
    turnirlar = db.get_turnirlar_list()
    index = next((i for i, t in enumerate(turnirlar) if t["id"] == turnir_id), None)

    if index is None:
        await _edit_caption(
            query, context,
            "😔 Ushbu turnir topilmadi (ehtimol o'chirilgan).",
            turnirlar_list_keyboard(turnirlar, is_admin),
        )
        return

    caption = _detail_caption(turnirlar, index)
    kb = turnirlar_detail_keyboard(turnirlar, index, is_admin)
    await _edit_caption(query, context, caption, kb)


async def on_turnir_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"turnir:nav:<index>" - Oldingi/Keyingi turnir tugmalari."""
    query = update.callback_query
    await query.answer()
    is_admin = _is_admin(query.from_user.id)

    index = int(query.data.split(":", 2)[2])
    turnirlar = db.get_turnirlar_list()

    if not turnirlar or not (0 <= index < len(turnirlar)):
        await _edit_caption(
            query, context, _list_caption(turnirlar), turnirlar_list_keyboard(turnirlar, is_admin)
        )
        return

    caption = _detail_caption(turnirlar, index)
    kb = turnirlar_detail_keyboard(turnirlar, index, is_admin)
    await _edit_caption(query, context, caption, kb)


async def on_turnir_back_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"turnir:list" - turnirlar ro'yxatiga qaytish."""
    query = update.callback_query
    await query.answer()
    is_admin = _is_admin(query.from_user.id)

    turnirlar = db.get_turnirlar_list()
    caption = _list_caption(turnirlar)
    kb = turnirlar_list_keyboard(turnirlar, is_admin)
    await _edit_caption(query, context, caption, kb)
