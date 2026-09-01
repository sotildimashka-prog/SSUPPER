# -*- coding: utf-8 -*-
"""💎 Almaz yechish - foydalanuvchi 'Tekin almaz'dan yig'gan almazlarini yechib olish.

🆕 Yangi oqim:
1) "💎 Almaz yechish" bosilganda avval foydalanuvchining O'ZINING HISOBI
   (joriy almaz balansi) ko'rsatiladi, pastida bitta "💎 Yechish" tugmasi
   chiqadi.
2) "💎 Yechish" bosilganda: agar balans 350 tadan KAM bo'lsa - "Almaz
   to'plang, minimal 350 almaz" degan ogohlantirish chiqadi va yechib
   bo'lmaydi. 350 yoki undan ko'p bo'lsa - avval Free Fire ID so'raladi,
   keyin "Necha dona almaz yechmoqchisiz?" deb so'raladi.
3) Foydalanuvchi miqdorni yozgach, so'rov ADMINGA "✅ Yubordim" tugmasi
   bilan boradi. Admin shu tugmani bosib, o'yin ichida almazni jo'natgach,
   foydalanuvchiga "✅ Almazlaringiz yuborildi" xabari avtomatik boradi.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    withdraw_account_keyboard,
    withdraw_not_enough_back_keyboard,
    withdraw_admin_review_keyboard,
)

WAITING_WITHDRAW_FF_ID = 40
WAITING_WITHDRAW_AMOUNT = 41

MIN_WITHDRAW = 350

NO_DIAMONDS_TEXT = (
    "💎 <b>Almaz yechish</b>\n\n"
    "Iltimos, botimizdan almaz to'plang 🙂\n"
    "Almazingiz yo'q. Almazni har xil o'yinlar (masalan 💎 Tekin almaz "
    "bo'limidagi savol-javoblar) bilan to'plashingiz mumkin."
)


def _account_text(amount: int) -> str:
    return (
        "💎 <b>Hisobim</b>\n\n"
        f"Sizda hozircha: <b>{amount}</b> dona almaz bor.\n\n"
        "Almazni yechib olish uchun pastdagi tugmani bosing 👇"
    )


def _not_enough_text(amount: int) -> str:
    return (
        "⚠️ <b>Almaz yechib bo'lmaydi</b>\n\n"
        f"❌ Yechish uchun kamida <b>{MIN_WITHDRAW}</b> ta almaz to'plashingiz kerak.\n"
        f"💎 Sizda hozircha: <b>{amount}</b> ta almaz bor.\n\n"
        "🎯 Ko'proq almaz to'plang va qaytadan urinib ko'ring!"
    )


async def _show_account(update_or_query, edit: bool):
    """"💎 Hisobim" ko'rinishini chiqaradi (matn + "Yechish" tugmasi)."""
    if edit:
        query = update_or_query
        user_id = query.from_user.id
        amount = db.get_quiz_diamonds(user_id)
        await query.edit_message_text(
            _account_text(amount), parse_mode="HTML", reply_markup=withdraw_account_keyboard()
        )
    else:
        update = update_or_query
        user_id = update.effective_user.id
        amount = db.get_quiz_diamonds(user_id)
        await update.message.reply_text(
            _account_text(amount), parse_mode="HTML", reply_markup=withdraw_account_keyboard()
        )


async def on_withdraw_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pastki (reply) "💎 Almaz yechish" tugmasi bosilganda."""
    await _show_account(update, edit=False)


async def on_withdraw_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👤 Profil / 🏆 Yutiqni chiqarish menyusidagi '💎 Almaz yechish' /
    '💎 Almaz chiqarish' tugmasi bosilganda - avval hisobim ko'rsatiladi."""
    query = update.callback_query
    await query.answer()
    await _show_account(query, edit=True)


async def on_withdraw_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"⬅️ Orqaga" - "Almaz yetarli emas" oynasidan "Hisobim" ko'rinishiga qaytish."""
    query = update.callback_query
    await query.answer()
    await _show_account(query, edit=True)


async def on_withdraw_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"💎 Yechish" tugmasi bosilganda: balans tekshiriladi, yetarli bo'lsa
    Free Fire ID so'raladi (ConversationHandler shu yerdan boshlanadi)."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    amount = db.get_quiz_diamonds(user_id)

    if amount < MIN_WITHDRAW:
        await query.edit_message_text(
            _not_enough_text(amount),
            parse_mode="HTML",
            reply_markup=withdraw_not_enough_back_keyboard(),
        )
        return ConversationHandler.END

    await query.edit_message_text(
        "🆔 Free Fire UID (ID) raqamingizni yuboring:\n\nBekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_WITHDRAW_FF_ID


async def receive_withdraw_ff_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ff_id = (update.message.text or "").strip()

    if not ff_id.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Faqat raqamlardan iborat Free Fire UID yuboring."
        )
        return WAITING_WITHDRAW_FF_ID

    context.user_data["withdraw_ff_id"] = ff_id

    amount = db.get_quiz_diamonds(update.effective_user.id)
    await update.message.reply_text(
        "💎 Necha dona almaz yechmoqchisiz?\n\n"
        f"(Kamida {MIN_WITHDRAW}, hisobingizda {amount} dona bor)\n\n"
        "Bekor qilish uchun /bekor.",
    )
    return WAITING_WITHDRAW_AMOUNT


async def receive_withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()
    is_admin = update.effective_user.id == ADMIN_ID
    user = update.effective_user

    if not raw.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Faqat raqam kiriting (masalan: 500)."
        )
        return WAITING_WITHDRAW_AMOUNT

    amount = int(raw)
    current = db.get_quiz_diamonds(user.id)

    if amount < MIN_WITHDRAW:
        await update.message.reply_text(
            f"⚠️ Kamida {MIN_WITHDRAW} dona almaz yechishingiz kerak. Qaytadan kiriting:"
        )
        return WAITING_WITHDRAW_AMOUNT

    if amount > current:
        await update.message.reply_text(
            f"⚠️ Sizda faqat {current} dona almaz bor. Qaytadan kiriting:"
        )
        return WAITING_WITHDRAW_AMOUNT

    ff_id = context.user_data.get("withdraw_ff_id", "")

    db.deduct_quiz_diamonds(user.id, amount)

    await update.message.reply_text(
        "✅ <b>So'rovingiz qabul qilindi!</b>\n\n"
        f"💎 <b>{amount}</b> dona almaz tez orada Free Fire hisobingizga o'tkaziladi.",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "💎 <b>Yangi almaz yechish so'rovi</b>\n\n"
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

    context.user_data.pop("withdraw_ff_id", None)
    return ConversationHandler.END


async def on_withdraw_sent_by_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin '✅ Yubordim' tugmasini bosganda - foydalanuvchiga xabar boradi."""
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu tugma faqat admin uchun.", show_alert=True)
        return
    await query.answer()

    parts = (query.data or "").split(":")
    # ["withdrawsent", user_id, amount, ff_id]
    if len(parts) < 4:
        return
    _, user_id_str, amount_str, ff_id = parts[0], parts[1], parts[2], ":".join(parts[3:])

    try:
        user_id = int(user_id_str)
        amount = int(amount_str)
    except ValueError:
        return

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 <b>Almazlaringiz yuborildi!</b>\n\n"
                f"💎 <b>{amount}</b> dona almaz Free Fire hisobingizga (UID: {ff_id}) "
                "muvaffaqiyatli o'tkazildi.\n"
                "Xizmatimizdan foydalanganingiz uchun rahmat! 🔥"
            ),
            parse_mode="HTML",
        )
    except TelegramError:
        pass

    try:
        await query.edit_message_text(
            (query.message.text or "") + "\n\n✅ <b>Yuborildi</b>", parse_mode="HTML"
        )
    except TelegramError:
        pass


async def cancel_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id == ADMIN_ID
    context.user_data.pop("withdraw_ff_id", None)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END
