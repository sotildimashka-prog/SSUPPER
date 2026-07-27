# -*- coding: utf-8 -*-
"""🛠 Admin buyrug'i - admin xohlagan foydalanuvchiga qo'lda pul yoki almaz yuboradi."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import main_menu_keyboard, admin_credit_type_keyboard

WAITING_CREDIT_AMOUNT, WAITING_CREDIT_USER_ID = range(30, 32)


async def on_admin_credit_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "🛠 <b>Admin buyrug'i</b>\n\nFoydalanuvchiga nima yubormoqchisiz?",
        parse_mode="HTML",
        reply_markup=admin_credit_type_keyboard(),
    )


async def on_credit_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    credit_type = query.data.split(":", 1)[1]  # "money" yoki "diamond"
    context.user_data["credit_type"] = credit_type

    label = "so'm (pul)" if credit_type == "money" else "dona almaz"
    await query.message.reply_text(
        f"💵 Qancha {label} yubormoqchisiz? (faqat raqam)\n\nBekor qilish uchun /bekor."
    )
    return WAITING_CREDIT_AMOUNT


async def receive_credit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip().replace(" ", "")
    if not raw.isdigit() or int(raw) <= 0:
        await update.message.reply_text("⚠️ Noto'g'ri format. Faqat musbat raqam kiriting.")
        return WAITING_CREDIT_AMOUNT

    context.user_data["credit_amount"] = int(raw)
    await update.message.reply_text(
        "🆔 Endi foydalanuvchining Telegram ID'sini yozing:\n\nBekor qilish uchun /bekor."
    )
    return WAITING_CREDIT_USER_ID


async def receive_credit_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()
    if not raw.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Faqat raqamlardan iborat Telegram ID yuboring."
        )
        return WAITING_CREDIT_USER_ID

    target_user_id = int(raw)
    credit_type = context.user_data.get("credit_type")
    amount = context.user_data.get("credit_amount")

    if not credit_type or not amount:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    if credit_type == "money":
        db.add_balance(target_user_id, amount)
        unit_text = f"{amount:,} so'm".replace(",", ".")
    else:
        db.add_quiz_diamonds(target_user_id, amount)
        unit_text = f"{amount} dona almaz"

    user_notify = f"🎉 Hisobingizga <b>{unit_text}</b> qo'shildi!"

    try:
        await context.bot.send_message(chat_id=target_user_id, text=user_notify, parse_mode="HTML")
        delivered = True
    except TelegramError:
        delivered = False

    status = (
        "✅ Foydalanuvchiga xabar yuborildi."
        if delivered
        else "⚠️ Foydalanuvchiga xabar yuborilmadi (botni bloklagan bo'lishi mumkin), "
        "lekin hisobiga muvaffaqiyatli qo'shildi."
    )
    await update.message.reply_text(
        f"✅ <b>{unit_text}</b> foydalanuvchi (<code>{target_user_id}</code>) hisobiga qo'shildi.\n\n{status}",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(True),
    )

    context.user_data.pop("credit_type", None)
    context.user_data.pop("credit_amount", None)
    return ConversationHandler.END


async def cancel_credit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("credit_type", None)
    context.user_data.pop("credit_amount", None)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True))
    return ConversationHandler.END
