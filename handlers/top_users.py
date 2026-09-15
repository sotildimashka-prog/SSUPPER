# -*- coding: utf-8 -*-
"""🏆 Top foydalanuvchilar - "Yordam" tugmasi tagida (bot ichidagi BARCHA
inline menyularda) chiqadigan ko'k tugma orqali ochiladi.

Uchta reyting ko'rsatiladi:
  - 💎 eng ko'p almaz yig'ganlar TOP 10;
  - 💰 eng ko'p pul yig'ganlar TOP 10;
  - 👥 eng ko'p referal (do'st) olib kelganlar TOP 10.

Reyting har safar qaytadan hisoblanmaydi - database.py dagi
`leaderboard_cache` jadvalidan o'qiladi. Kesh bot ishga tushganda,
har kuni (bot.py dagi JobQueue vazifasi orqali) va admin panelidagi
"🔄 Top yangilash" tugmasi bosilganda avtomatik yangilanadi.
"""

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from config import ADMIN_ID
from handlers.message_utils import safe_edit_message
from keyboards import (
    top_users_keyboard,
    TOP_USERS_DIAMOND_CB,
    TOP_USERS_MONEY_CB,
)

_MEDALS = ("🥇", "🥈", "🥉")


def _format_updated_at(updated_at: str | None) -> str:
    if not updated_at:
        return "hali yangilanmagan"
    # "2026-09-13T10:15:00.123456" -> "2026-09-13 10:15"
    return updated_at.replace("T", " ")[:16]


def _format_list(entries: list, unit_label: str, unit_emoji: str) -> str:
    if not entries:
        return "😔 Hozircha bu reytingda hech kim yo'q."
    lines = []
    for i, entry in enumerate(entries, start=1):
        rank = _MEDALS[i - 1] if i <= 3 else f"{i}."
        lines.append(f"{rank} {entry['name']} — {entry['value']} {unit_emoji}")
    return "\n".join(lines)


def _build_text(active: str) -> str:
    if active == "dia":
        entries, updated_at = db.get_cached_leaderboard("top_diamonds")
        body = _format_list(entries, "almaz", "💎")
        title = "💎 <b>Eng ko'p almaz yig'ganlar</b>"
    elif active == "money":
        entries, updated_at = db.get_cached_leaderboard("top_money")
        body = _format_list(entries, "so'm", "💰")
        title = "💰 <b>Eng ko'p pul yig'ganlar</b>"
    else:
        entries, updated_at = db.get_cached_leaderboard("top_referrers")
        body = _format_list(entries, "referal", "👥")
        title = "👥 <b>Eng ko'p referal olib kelganlar</b>"

    return (
        "🏆 <b>TOP FOYDALANUVCHILAR</b>\n\n"
        f"{title}\n\n"
        f"{body}\n\n"
        f"🔄 So'nggi yangilanish: {_format_updated_at(updated_at)}\n"
        "📅 Reyting har kuni avtomatik yangilanadi."
    )


async def on_top_users_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"🏆 Top foydalanuvchilar" tugmasi bosilganda - default holatda
    almazlar reytingi ko'rsatiladi."""
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query,
        _build_text("dia"),
        parse_mode="HTML",
        reply_markup=top_users_keyboard("dia"),
    )


async def on_top_users_tab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💎 Almazlar / 💰 Pul / 👥 Referallar tab tugmalari."""
    query = update.callback_query
    await query.answer()
    if query.data == TOP_USERS_DIAMOND_CB:
        active = "dia"
    elif query.data == TOP_USERS_MONEY_CB:
        active = "money"
    else:
        active = "ref"
    await safe_edit_message(
        query,
        _build_text(active),
        parse_mode="HTML",
        reply_markup=top_users_keyboard(active),
    )


# ==================== 🔄 Top yangilash (faqat admin) ====================

async def on_top_refresh_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panelidagi "🔄 Top yangilash" tugmasi. Bosilganda uchala
    reyting (💎 almaz, 💰 pul, 👥 referal) bazadan qaytadan hisoblanib,
    keshga yoziladi va natija darhol adminga ko'rsatiladi."""
    if not update.effective_user or update.effective_user.id != ADMIN_ID:
        return

    status = await update.message.reply_text("⏳ Top ro'yxatlar yangilanmoqda...")

    top_referrers, top_diamonds, top_money = db.refresh_leaderboard_cache()

    text = (
        "✅ <b>Top foydalanuvchilar yangilandi!</b>\n\n"
        "💎 <b>Eng ko'p almaz yig'ganlar</b>\n"
        f"{_format_list(top_diamonds, 'almaz', '💎')}\n\n"
        "💰 <b>Eng ko'p pul yig'ganlar</b>\n"
        f"{_format_list(top_money, 'som', '💰')}\n\n"
        "👥 <b>Eng ko'p referral olib kelganlar</b>\n"
        f"{_format_list(top_referrers, 'referal', '👥')}"
    )

    try:
        await status.edit_text(text, parse_mode="HTML")
    except Exception:
        await update.message.reply_text(text, parse_mode="HTML")
