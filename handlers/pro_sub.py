# -*- coding: utf-8 -*-
"""👑 Pro obuna - bosh menyudagi yangi bo'lim.

Foydalanuvchiga Pro tarifning imkoniyatlarini rasm bilan birga ko'rsatadi.
"Tarifni sotib olish" tugmasi bosilganda:
  - Agar hisobida yetarli mablag' (PRO_SUB_PRICE) bo'lsa -> summa avtomatik
    yechiladi, Pro obuna faollashtiriladi va foydalanuvchiga maxsus
    "PRO OBUNA" bo'limi (qizil tugmalar bilan) ochiladi.
  - Agar mablag' yetarli bo'lmasa -> hisobni to'ldirish (Admin / Humo-Uzcard)
    menyusiga o'tkaziladi.
"""

import os

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

import database as db
from keyboards import (
    pro_sub_keyboard,
    pro_sub_active_keyboard,
    account_keyboard,
    back_reply_keyboard,
)

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

PRO_WELCOME_TEXT = (
    "👑 <b>Yangi bo'limga xush kelibsiz!</b>\n\n"
    "Siz <b>PRO OBUNA</b> bo'limidasiz. 🎉\n\n"
    "Quyidagi maxsus imkoniyatlardan foydalanishingiz mumkin 👇"
)


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
    """💳 Tarifni sotib olish.

    Hisobida yetarli mablag' bo'lsa - avtomatik yechib, Pro obunani
    faollashtiradi va maxsus bo'limni ochadi. Aks holda hisobni to'ldirish
    menyusiga yo'naltiradi.
    """
    query = update.callback_query
    user = query.from_user
    balance = db.get_balance(user.id)

    if balance < PRO_SUB_PRICE:
        await query.answer(
            "⛔️ Hisobingizda mablag' yetarli emas.", show_alert=True
        )
        text = (
            "💰 <b>Hisobni to'ldirish</b>\n\n"
            f"👑 Pro tarif narxi: <b>{PRO_SUB_PRICE:,} so'm</b>\n"
            f"💳 Sizning hisobingiz: <b>{balance:,} so'm</b>\n\n".replace(",", ".")
            + "Hisobingizni qanday to'ldirmoqchisiz? 👇"
        )
        await context.bot.send_message(
            chat_id=user.id,
            text=text,
            parse_mode="HTML",
            reply_markup=account_keyboard(),
        )
        return

    ok = db.deduct_balance(user.id, PRO_SUB_PRICE)
    if not ok:
        await query.answer(
            "⛔️ Hisobingizda mablag' yetarli emas.", show_alert=True
        )
        return

    db.set_pro_user(user.id, True)
    await query.answer("✅ Pro obuna muvaffaqiyatli faollashtirildi!", show_alert=True)

    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=PRO_WELCOME_TEXT,
            parse_mode="HTML",
            reply_markup=pro_sub_active_keyboard(),
        )
    except TelegramError:
        pass
