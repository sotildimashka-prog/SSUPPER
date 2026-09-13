# -*- coding: utf-8 -*-
"""🏆 Top foydalanuvchilar - "Yordam" tugmasi tagida (bot ichidagi BARCHA
inline menyularda) chiqadigan ko'k tugma orqali ochiladi.

Ikkita reyting ko'rsatiladi:
  - 👥 eng ko'p referal (do'st) olib kelganlar TOP 10;
  - 💎 eng ko'p almaz yig'ganlar TOP 10.

Reyting har safar qaytadan hisoblanmaydi - database.py dagi
`leaderboard_cache` jadvalidan o'qiladi. Kesh bot ishga tushganda va
har kuni (bot.py dagi JobQueue vazifasi orqali) avtomatik yangilanadi.
"""

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from handlers.message_utils import safe_edit_message
from keyboards import top_users_keyboard, TOP_USERS_DIAMOND_CB

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
    referallar reytingi ko'rsatiladi."""
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query,
        _build_text("ref"),
        parse_mode="HTML",
        reply_markup=top_users_keyboard("ref"),
    )


async def on_top_users_tab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👥 Referallar / 💎 Almazlar tab tugmalari."""
    query = update.callback_query
    await query.answer()
    active = "dia" if query.data == TOP_USERS_DIAMOND_CB else "ref"
    await safe_edit_message(
        query,
        _build_text(active),
        parse_mode="HTML",
        reply_markup=top_users_keyboard(active),
    )
