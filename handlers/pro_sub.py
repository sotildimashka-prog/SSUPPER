# -*- coding: utf-8 -*-
"""👑 Pro obuna - bosh menyudagi yangi bo'lim.

Foydalanuvchiga Pro tarifning imkoniyatlarini rasm bilan birga ko'rsatadi.
"Tarifni sotib olish" tugmasi bosilganda avtomatik ravishda hisobni
to'ldirish (Admin / Humo-Uzcard) menyusiga o'tkaziladi.
"""

import os

from telegram import Update
from telegram.ext import ContextTypes

from keyboards import pro_sub_keyboard, account_keyboard, back_reply_keyboard

PRO_SUB_IMAGE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "pro_obuna.jpg"
)

PRO_SUB_PRICE = 39_000

PRO_SUB_TEXT = (
    "👑 <b>PRO OBUNA</b>\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    f"Siz birgina Pro tarifni <b>{PRO_SUB_PRICE:,} so'm</b>ga sotib olsangiz, "
    "quyidagi imkoniyatlarga ega bo'lasiz:\n\n"
    "✨ Super nastroyka/nik yaratish\n"
    "🎬 AI video yasash\n"
    "🏆 Botta 1-o'rin mukofotini olish\n"
    "🎁 Sirli sovg'a\n\n"
    "━━━━━━━━━━━━━━━━━━"
).replace(",", ".")


async def on_pro_sub_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👑 Pro obuna (Reply tugma)."""
    try:
        with open(PRO_SUB_IMAGE, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=PRO_SUB_TEXT,
                parse_mode="HTML",
                reply_markup=pro_sub_keyboard(),
            )
    except (FileNotFoundError, OSError):
        await update.message.reply_text(
            PRO_SUB_TEXT, parse_mode="HTML", reply_markup=pro_sub_keyboard()
        )

    await update.message.reply_text(
        "⬅️ Orqaga qaytish uchun pastdagi tugmani bosing.",
        reply_markup=back_reply_keyboard(),
    )


async def on_prosub_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💳 Tarifni sotib olish - avtomatik hisob to'ldirish menyusiga o'tadi."""
    query = update.callback_query
    await query.answer()

    text = (
        "💰 <b>Hisobni to'ldirish</b>\n\n"
        f"👑 Pro tarif narxi: <b>{PRO_SUB_PRICE:,} so'm</b>\n\n".replace(",", ".")
        + "Hisobingizni qanday to'ldirmoqchisiz? 👇"
    )

    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=text,
        parse_mode="HTML",
        reply_markup=account_keyboard(),
    )
