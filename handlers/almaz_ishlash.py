# -*- coding: utf-8 -*-
"""🍎 ALMAZ ISHLASH bo'limi - Olma yig'ish va Referal tizimi.

Oqim:
1) Kirish sahifasi - qisqa va kreativ tanishtiruv (➡️ Keyingisi)
2) Referal haqida - unikal havola va mukofot tushuntirilishi (🔙 Ortga / ➡️ Keyingisi)
3) 🍎 Olma haqida - bonus birligi tushuntirilishi (🔙 Ortga / 🔵 🍎 Olma ishlash)
4) Olma ishlash paneli - shaxsiy referal havola + joriy 🍎 balans (🔙 Ortga)
5) 👤 Hisobim - referal statistikasi (havolalar, do'stlar, jarimalar,
   olmalar, almazlar)

Referal mukofoti (+2 🍎 ikkalasiga ham) foydalanuvchi majburiy kanallarga
obuna bo'lishni yakunlagach beriladi - buning uchun handlers/start.py da
db.credit_referral_if_pending(...) chaqiriladi.

⚠️ Jarima: agar do'st mukofot olingandan so'ng REFERRAL_PENALTY_CHECK_HOURS
soat ichida (taxminan 1-2 kun) majburiy kanallardan chiqib ketsa,
check_referral_penalties_job (JobQueue orqali davriy ishga tushadi)
buni aniqlab, ikkala tomondan ham 🍎 ayiradi.
"""

from telegram.error import TelegramError
from telegram.ext import ContextTypes

from handlers.message_utils import safe_edit_message
from handlers.subscription import get_unsubscribed_channels
import database as db
from keyboards import (
    almaz_page1_keyboard,
    almaz_page2_keyboard,
    almaz_page3_keyboard,
    almaz_dashboard_keyboard,
    almaz_account_keyboard,
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
    "Qancha ko'p do'st taklif qilsangiz - shuncha ko'p 🍎 yig'asiz!\n\n"
    "⚠️ <b>Diqqat:</b> agar do'stingiz mukofot olingandan keyin 1-2 kun "
    "ichida majburiy kanallardan chiqib ketsa, jarima qo'llanadi va "
    "ikkalangizning hisobidan ham 2 🍎 dan ayriladi."
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


async def _get_referral_link(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> str:
    me = await context.bot.get_me()
    return f"https://t.me/{me.username}?start=ref{user_id}"


def _dashboard_text(link: str, apples: int, invited: int) -> str:
    return (
        "🔗 <b>REFERAL HAVOLASI</b>\n\n"
        "Sizning referal havolangiz:\n"
        f"<code>{link}</code>\n\n"
        f"🍎 Joriy olmalaringiz: <b>{apples}</b>\n"
        f"👥 Taklif qilingan do'stlar: <b>{invited}</b>\n\n"
        f"💡 Har <b>{db.APPLE_TO_DIAMOND_RATE}</b> dona 🍎 = "
        f"<b>{db.APPLE_TO_DIAMOND_YIELD}</b> dona 💎.\n\n"
        "Havolani do'stlaringizga ulashing va 🍎 yig'ishda davom eting! 🚀"
    )


async def on_almaz_dashboard(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    link = await _get_referral_link(context, user_id)
    apples = db.get_apples(user_id)
    invited = db.count_referrals(user_id)

    text = _dashboard_text(link, apples, invited)
    await safe_edit_message(
        query, text, parse_mode="HTML", reply_markup=almaz_dashboard_keyboard(link)
    )


def _account_text(link_count: int, invited: int, penalties: int, apples: int, diamonds: int) -> str:
    return (
        "👤 <b>HISOBIM</b>\n\n"
        f"🔗 Referal havolalar: <b>{link_count}</b>\n"
        f"👥 Taklif qilingan do'stlar: <b>{invited}</b>\n"
        f"⚠️ Jarimalar: <b>{penalties}</b>\n"
        f"🍎 Olmalar: <b>{apples}</b>\n"
        f"💎 Almazlar: <b>{diamonds}</b>"
    )


async def on_almaz_account(update, context: ContextTypes.DEFAULT_TYPE):
    """👤 Hisobim tugmasi bosilganda - referal statistikasi."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    link_count = db.count_referral_links(user_id)
    invited = db.count_referrals(user_id)
    penalties = db.get_penalties(user_id)
    apples = db.get_apples(user_id)
    diamonds = db.get_quiz_diamonds(user_id)

    text = _account_text(link_count, invited, penalties, apples, diamonds)
    await safe_edit_message(
        query, text, parse_mode="HTML", reply_markup=almaz_account_keyboard()
    )


async def on_almaz_convert(update, context: ContextTypes.DEFAULT_TYPE):
    """💎 Olmalarni almazga aylantirish tugmasi bosilganda."""
    query = update.callback_query
    user_id = query.from_user.id
    group_size = db.APPLE_TO_DIAMOND_RATE
    yield_per_group = db.APPLE_TO_DIAMOND_YIELD

    diamonds, used = db.convert_apples_to_diamonds(user_id, group_size, yield_per_group)

    if diamonds <= 0:
        await query.answer(
            f"⚠️ Aylantirish uchun kamida {group_size} dona 🍎 kerak. "
            f"Ko'proq do'st taklif qiling!",
            show_alert=True,
        )
        return

    await query.answer(
        f"🎉 {used} dona 🍎 ➜ {diamonds} dona 💎 ga aylantirildi!",
        show_alert=True,
    )

    link = await _get_referral_link(context, user_id)
    apples = db.get_apples(user_id)
    invited = db.count_referrals(user_id)
    text = _dashboard_text(link, apples, invited)
    await safe_edit_message(
        query, text, parse_mode="HTML", reply_markup=almaz_dashboard_keyboard(link)
    )


# ==================== ⚠️ Jarima tizimi (davriy tekshiruv) ====================

_PENALTY_MSG_TO_FRIEND = (
    "⚠️ <b>Jarima qo'llandi!</b>\n\n"
    "Siz taklif qilingan majburiy kanallardan chiqib ketganingiz sababli, "
    "sizning va do'stingizning hisobidan {amount} 🍎 dan ayrildi."
)
_PENALTY_MSG_TO_REFERRER = (
    "⚠️ <b>Jarima qo'llandi!</b>\n\n"
    "Taklif qilgan do'stingiz majburiy kanallardan chiqib ketgani sababli, "
    "sizning va uning hisobidan {amount} 🍎 dan ayrildi."
)


async def check_referral_penalties_job(context: ContextTypes.DEFAULT_TYPE):
    """JobQueue orqali davriy chaqiriladi: mukofot berilgan referallardan
    tekshiruv vaqti (REFERRAL_PENALTY_CHECK_HOURS) yetganlarini olib,
    hali ham majburiy kanallarga obuna ekanini tekshiradi. Agar do'st
    chiqib ketgan bo'lsa - ikkala tomondan ham 🍎 ayiradi."""
    pending = db.get_pending_penalty_checks()
    amount = db.REFERRAL_PENALTY_APPLES

    for referred_id, referrer_id in pending:
        try:
            unsubscribed = await get_unsubscribed_channels(
                referred_id, context, use_cache=False
            )
        except Exception:
            # Tekshirib bo'lmadi (masalan foydalanuvchi botni bloklagan) -
            # keyingi safar qayta urinish uchun hozircha o'tkazib yuboramiz.
            continue

        if not unsubscribed:
            # Hali ham obuna - jarima yo'q, faqat tekshirilgan deb belgilanadi.
            db.mark_penalty_checked(referred_id)
            continue

        db.apply_referral_penalty(referred_id, referrer_id, amount)

        for uid, template in (
            (referred_id, _PENALTY_MSG_TO_FRIEND),
            (referrer_id, _PENALTY_MSG_TO_REFERRER),
        ):
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=template.format(amount=amount),
                    parse_mode="HTML",
                )
            except TelegramError:
                pass
