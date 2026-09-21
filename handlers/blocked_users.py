# -*- coding: utf-8 -*-
"""🚫 Bloklanganlar - faqat admin uchun.

Admin panelidagi "🚫 Bloklanganlar" tugmasi botdan bloklangan foydalanuvchilar
ro'yxatini ko'rsatadi. Har bir foydalanuvchini ochib, uni blokdan chiqarish
yoki (blokdan chiqarilgan bo'lsa) qayta bloklash mumkin.
"""

import html
import math

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import (
    BLOCKED_PAGE_SIZE,
    blocked_user_display_name,
    blocked_users_list_keyboard,
    blocked_user_detail_keyboard,
)


def _fmt_time(value) -> str:
    """ISO vaqtni (UTC) '2026-09-21 10:30' ko'rinishiga keltiradi."""
    if not value:
        return "—"
    return str(value)[:16].replace("T", " ")


def _list_view(page: int):
    """(matn, klaviatura, to'g'rilangan sahifa raqami)."""
    active, total = db.count_blocked_users()
    total_pages = max(1, math.ceil(total / BLOCKED_PAGE_SIZE))
    page = min(max(page, 0), total_pages - 1)
    rows = db.get_blocked_users(limit=BLOCKED_PAGE_SIZE, offset=page * BLOCKED_PAGE_SIZE)

    if total == 0:
        text = (
            "🚫 <b>Bloklanganlar</b>\n\n"
            "Hozircha hech kim bloklanmagan.\n\n"
            "Foydalanuvchini bloklash uchun pastdagi tugmani bosing."
        )
    else:
        text = (
            "🚫 <b>Bloklanganlar</b>\n\n"
            f"🚫 Hozir bloklangan: <b>{active}</b>\n"
            f"✅ Blokdan chiqarilgan: <b>{total - active}</b>\n\n"
            "Foydalanuvchini tanlang 👇"
        )
    return text, blocked_users_list_keyboard(rows, page, total_pages), page


def _detail_view(user_id: int, page: int):
    """(matn, klaviatura) yoki (None, None) agar yozuv topilmasa."""
    row = db.get_blocked_user(user_id)
    if not row:
        return None, None

    name = html.escape(blocked_user_display_name(row))
    username = f"@{html.escape(row['username'])}" if row["username"] else "—"
    is_active = bool(row["is_active"])
    status = "🚫 <b>Bloklangan</b>" if is_active else "✅ <b>Blokdan chiqarilgan</b>"

    lines = [
        "👤 <b>Foydalanuvchi</b>\n",
        f"Ism: {name}",
        f"Username: {username}",
        f"ID: <code>{row['user_id']}</code>",
        f"Holati: {status}",
        f"Bloklangan vaqti: {_fmt_time(row['blocked_at'])} (UTC)",
    ]
    if not is_active:
        lines.append(f"Blokdan chiqarilgan: {_fmt_time(row['unblocked_at'])} (UTC)")

    return "\n".join(lines), blocked_user_detail_keyboard(row["user_id"], is_active, page)


async def _edit(query, text: str, keyboard):
    try:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
    except TelegramError:
        # "message is not modified" kabi zararsiz xatolar e'tiborsiz qoldiriladi
        pass


async def on_blocked_users_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin paneli: 🚫 Bloklanganlar tugmasi."""
    if update.effective_user.id != ADMIN_ID:
        return
    text, keyboard, _ = _list_view(0)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)


async def on_blocked_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """blk:* inline tugmalari (ro'yxat, sahifalash, ochish, bloklash, yopish)."""
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return

    parts = (query.data or "").split(":")
    action = parts[1] if len(parts) > 1 else ""

    def _int(index: int, default: int = 0) -> int:
        try:
            return int(parts[index])
        except (IndexError, ValueError):
            return default

    if action == "noop":
        await query.answer()
        return

    if action == "close":
        await query.answer()
        try:
            await query.message.delete()
        except TelegramError:
            pass
        return

    if action == "list":
        await query.answer()
        text, keyboard, _ = _list_view(_int(2))
        await _edit(query, text, keyboard)
        return

    if action == "view":
        user_id, page = _int(2), _int(3)
        text, keyboard = _detail_view(user_id, page)
        if text is None:
            await query.answer("Foydalanuvchi ro'yxatda topilmadi.", show_alert=True)
            list_text, list_kb, _ = _list_view(page)
            await _edit(query, list_text, list_kb)
            return
        await query.answer()
        await _edit(query, text, keyboard)
        return

    if action in ("unblock", "block"):
        user_id, page = _int(2), _int(3)
        if not user_id:
            await query.answer()
            return
        if action == "unblock":
            db.unblock_user(user_id)
            await query.answer("✅ Blokdan chiqarildi.")
        else:
            db.block_user(user_id)
            await query.answer("🚫 Qayta bloklandi.")
        text, keyboard = _detail_view(user_id, page)
        if text is None:
            text, keyboard, _ = _list_view(page)
        await _edit(query, text, keyboard)
        return

    await query.answer()
