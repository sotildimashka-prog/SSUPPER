# -*- coding: utf-8 -*-
"""🎁 Sovg'alar - bosh menyudagi yangi bo'lim.

Uch xil sovg'a turini bitta joyga jamlaydi:
  - 🆓 Tekin almaz   -> savol-javob (quiz) orqali almaz ishlab olish
  - 💵 Pul bonusi    -> kunlik avtomatik pul bonusi
  - 🌙 Almaz bonusi  -> kunlik bonus almaz (admin tomonidan "Hammaga sovg'a"
                        buyrug'i orqali ham qo'shimcha almaz berilishi mumkin)
"""

from telegram import Update
from telegram.ext import ContextTypes

from keyboards import gifts_keyboard
from handlers.quiz import on_quiz_button_callback
from handlers.newflow import on_pay_daily_bonus, on_pay_bonus_diamond

GIFTS_TEXT = (
    "🎁 <b>Sovg'alar</b>\n\n"
    "Bu yerda botimizdan bepul almaz va bonuslar olishingiz mumkin 👇"
)


async def on_gifts_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        GIFTS_TEXT, parse_mode="HTML", reply_markup=gifts_keyboard()
    )


async def on_gift_free_diamond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🆓 Tekin almaz - mavjud savol-javob (quiz) oqimi qayta ishlatiladi."""
    await on_quiz_button_callback(update, context)


async def on_gift_money_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💵 Pul bonusi - mavjud kunlik pul bonusi oqimi qayta ishlatiladi."""
    await on_pay_daily_bonus(update, context)


async def on_gift_diamond_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🌙 Almaz bonusi - mavjud kunlik almaz bonusi oqimi qayta ishlatiladi."""
    await on_pay_bonus_diamond(update, context)
