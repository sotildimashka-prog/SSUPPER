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

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes, ConversationHandler

from handlers.message_utils import safe_edit_message
from handlers.subscription import get_unsubscribed_channels
import database as db
from config import ADMIN_ID
from keyboards import (
    almaz_page1_keyboard,
    almaz_page2_keyboard,
    almaz_page3_keyboard,
    almaz_dashboard_keyboard,
    almaz_account_keyboard,
    almaz_withdraw_account_keyboard,
    almaz_withdraw_not_enough_keyboard,
    almaz_withdraw_cancel_keyboard,
    withdraw_admin_review_keyboard,
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


# ==================== 💎 Almaz yechish (Referal berish bo'limi ichidan) ====================

WAITING_ALMAZWD_FF_ID = 210
WAITING_ALMAZWD_AMOUNT = 211

MIN_ALMAZ_WITHDRAW = 200

NOT_ENOUGH_ALMAZWD_TEXT = (
    "💎 Hisobingizda almaz yetarli emas. Minimum 200 almaz yig'ing."
)


def _almazwd_account_text(diamonds: int) -> str:
    return (
        "💎 <b>Almaz yechish</b>\n\n"
        f"Jami almazlaringiz: <b>{diamonds}</b> 💎\n\n"
        "Yechib olish uchun pastdagi tugmani bosing 👇"
    )


async def on_almaz_withdraw_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💎 Almaz yechish tugmasi (referal berish bo'limida) bosilganda -
    foydalanuvchining jami almazi va "Almazimni yechish" tugmasi chiqadi."""
    query = update.callback_query
    await query.answer()

    diamonds = db.get_quiz_diamonds(query.from_user.id)
    await safe_edit_message(
        query,
        _almazwd_account_text(diamonds),
        parse_mode="HTML",
        reply_markup=almaz_withdraw_account_keyboard(),
    )


async def on_almaz_withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💎 Almazimni yechish tugmasi - 200+ bo'lsa ID so'raladi, aks holda
    "almaz yetarli emas" xabari chiqadi."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    diamonds = db.get_quiz_diamonds(user_id)

    if diamonds < MIN_ALMAZ_WITHDRAW:
        await safe_edit_message(
            query,
            NOT_ENOUGH_ALMAZWD_TEXT,
            reply_markup=almaz_withdraw_not_enough_keyboard(),
        )
        return ConversationHandler.END

    await safe_edit_message(
        query,
        "🆔 Free Fire UID (ID) raqamingizni yuboring:\n\n"
        "Bekor qilish uchun /bekor yozing yoki pastdagi tugmani bosing.",
        reply_markup=almaz_withdraw_cancel_keyboard(),
    )
    return WAITING_ALMAZWD_FF_ID


async def receive_almazwd_ff_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ff_id = (update.message.text or "").strip()

    if not ff_id.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Faqat raqamlardan iborat Free Fire UID yuboring.",
            reply_markup=almaz_withdraw_cancel_keyboard(),
        )
        return WAITING_ALMAZWD_FF_ID

    context.user_data["almazwd_ff_id"] = ff_id

    diamonds = db.get_quiz_diamonds(update.effective_user.id)
    await update.message.reply_text(
        "💎 Necha dona almaz yechmoqchisiz?\n\n"
        f"(Kamida {MIN_ALMAZ_WITHDRAW}, hisobingizda {diamonds} dona bor)\n\n"
        "Bekor qilish uchun /bekor yozing yoki pastdagi tugmani bosing.",
        reply_markup=almaz_withdraw_cancel_keyboard(),
    )
    return WAITING_ALMAZWD_AMOUNT


async def receive_almazwd_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()
    user = update.effective_user

    if not raw.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Faqat raqam kiriting (masalan: 500).",
            reply_markup=almaz_withdraw_cancel_keyboard(),
        )
        return WAITING_ALMAZWD_AMOUNT

    amount = int(raw)
    current = db.get_quiz_diamonds(user.id)

    if amount < MIN_ALMAZ_WITHDRAW:
        await update.message.reply_text(
            f"⚠️ Kamida {MIN_ALMAZ_WITHDRAW} dona almaz yechishingiz kerak. Qaytadan kiriting:",
            reply_markup=almaz_withdraw_cancel_keyboard(),
        )
        return WAITING_ALMAZWD_AMOUNT

    if amount > current:
        await update.message.reply_text(
            f"⚠️ Sizda faqat {current} dona almaz bor. Qaytadan kiriting:",
            reply_markup=almaz_withdraw_cancel_keyboard(),
        )
        return WAITING_ALMAZWD_AMOUNT

    ff_id = context.user_data.get("almazwd_ff_id", "")
    db.deduct_quiz_diamonds(user.id, amount)

    await update.message.reply_text(
        "✅ <b>So'rovingiz qabul qilindi!</b>\n\n"
        f"💎 <b>{amount}</b> dona almaz tez orada Free Fire hisobingizga o'tkaziladi.",
        parse_mode="HTML",
    )

    admin_text = (
        "💎 <b>Yangi almaz yechish so'rovi (Referal bo'limi)</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"🎮 Free Fire UID: <code>{ff_id}</code>\n"
        f"💎 Miqdor: <b>{amount}</b> dona almaz\n\n"
        "Yuborgach, pastdagi tugmani bosing 👇"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=withdraw_admin_review_keyboard(user.id, amount, ff_id),
        )
    except TelegramError:
        pass

    context.user_data.pop("almazwd_ff_id", None)
    return ConversationHandler.END


async def on_almaz_withdraw_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("almazwd_ff_id", None)
    diamonds = db.get_quiz_diamonds(query.from_user.id)
    await safe_edit_message(
        query,
        _almazwd_account_text(diamonds),
        parse_mode="HTML",
        reply_markup=almaz_withdraw_account_keyboard(),
    )
    return ConversationHandler.END


async def cancel_almazwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("almazwd_ff_id", None)
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END


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
