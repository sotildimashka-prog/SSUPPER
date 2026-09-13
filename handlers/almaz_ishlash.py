# -*- coding: utf-8 -*-
"""🍎 ALMAZ ISHLASH bo'limi - Olma yig'ish va Referal tizimi.

Oqim:
1) Kirish sahifasi - qisqa va kreativ tanishtiruv (➡️ Keyingisi)
2) Referal haqida - unikal havola va mukofot tushuntirilishi (🔙 Ortga / ➡️ Keyingisi)
3) 🍎 Olma haqida - bonus birligi tushuntirilishi (🔙 Ortga / 🔵 🍎 Olma ishlash)
4) Olma ishlash paneli - shaxsiy referal havola + joriy 🍎 balans (🔙 Ortga)

Referal mukofoti (+2 🍎 ikkalasiga ham) foydalanuvchi majburiy kanallarga
obuna bo'lishni yakunlagach beriladi - buning uchun handlers/start.py da
db.credit_referral_if_pending(...) chaqiriladi.
"""

from telegram.ext import ContextTypes

from handlers.message_utils import safe_edit_message
import database as db
from keyboards import (
    almaz_page1_keyboard,
    almaz_page2_keyboard,
    almaz_page3_keyboard,
    almaz_dashboard_keyboard,
)

PAGE1_TEXT = (
    "🍎✨ <b>ALMAZ ISHLASH</b> ✨🍎\n\n"
    "Assalomu alaykum, jasur jangchi! 🎮🔥\n\n"
    "Bilasizmi? Endi 💎 <b>Almazni</b> pulsiz ham qo'lga kiritish mumkin!\n\n"
    "🍎 Bot orqali <b>olma</b> yig'asiz, so'ng ularni keyinchalik "
    "💎 <b>Almazga</b> aylantirasiz — hammasi bepul, hammasi sizning "
    "qo'lingizda! 🚀\n\n"
    "Qiziqmi? Unda davom etamiz 👇"
)

PAGE2_TEXT = (
    "🔗 <b>Referal haqida</b>\n\n"
    "Har bir foydalanuvchiga alohida, faqat o'ziga tegishli 🔗 <b>unikal "
    "havola</b> beriladi.\n\n"
    "📤 Shu havolani do'stlaringizga yuboring.\n"
    "👋 Do'stingiz havola orqali <b>/start</b> bosib botga kirsin.\n"
    "📢 Ikkalangiz ham majburiy kanallarga obuna bo'lgach:\n\n"
    "➕ Sizga: <b>2 🍎</b>\n"
    "➕ Taklif qilingan do'stingizga: <b>2 🍎</b>\n\n"
    "Qancha ko'p do'st taklif qilsangiz - shuncha ko'p 🍎 yig'asiz!"
)

PAGE3_TEXT = (
    "🍎 <b>Olma nima?</b>\n\n"
    "🍏 Olma - botimizdagi maxsus bonus hisob birligi.\n"
    "💎 Yig'ilgan olmalarni keyinchalik <b>Almazga</b> aylantirish mumkin "
    "bo'ladi.\n\n"
    "Har bir olma - 💎 tomon bir qadam! Tayyor bo'lsangiz, pastdagi "
    "tugmani bosing 👇"
)


async def on_almaz_page1(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query, PAGE1_TEXT, parse_mode="HTML", reply_markup=almaz_page1_keyboard()
    )


async def on_almaz_page2(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query, PAGE2_TEXT, parse_mode="HTML", reply_markup=almaz_page2_keyboard()
    )


async def on_almaz_page3(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query, PAGE3_TEXT, parse_mode="HTML", reply_markup=almaz_page3_keyboard()
    )


def _dashboard_text(link: str, apples: int, invited: int) -> str:
    return (
        "🍎 <b>Olma ishlash</b>\n\n"
        "🔗 Sizning shaxsiy havolangiz:\n"
        f"<code>{link}</code>\n\n"
        f"🍎 Joriy olmalaringiz: <b>{apples}</b>\n"
        f"👥 Taklif qilingan do'stlar: <b>{invited}</b>\n\n"
        f"💡 Har <b>{db.APPLE_TO_DIAMOND_RATE}</b> dona 🍎 = <b>1</b> dona 💎.\n\n"
        "Havolani do'stlaringizga ulashing va 🍎 yig'ishda davom eting! 🚀"
    )


async def on_almaz_dashboard(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    me = await context.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref{user_id}"
    apples = db.get_apples(user_id)
    invited = db.count_referrals(user_id)

    text = _dashboard_text(link, apples, invited)
    await safe_edit_message(
        query, text, parse_mode="HTML", reply_markup=almaz_dashboard_keyboard()
    )


async def on_almaz_convert(update, context: ContextTypes.DEFAULT_TYPE):
    """💎 Olmalarni almazga aylantirish tugmasi bosilganda."""
    query = update.callback_query
    user_id = query.from_user.id
    rate = db.APPLE_TO_DIAMOND_RATE

    diamonds, used = db.convert_apples_to_diamonds(user_id, rate)

    if diamonds <= 0:
        await query.answer(
            f"⚠️ Aylantirish uchun kamida {rate} dona 🍎 kerak. "
            f"Ko'proq do'st taklif qiling!",
            show_alert=True,
        )
        return

    await query.answer(
        f"🎉 {used} dona 🍎 ➜ {diamonds} dona 💎 ga aylantirildi!",
        show_alert=True,
    )

    me = await context.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref{user_id}"
    apples = db.get_apples(user_id)
    invited = db.count_referrals(user_id)
    text = _dashboard_text(link, apples, invited)
    await safe_edit_message(
        query, text, parse_mode="HTML", reply_markup=almaz_dashboard_keyboard()
    )
