# -*- coding: utf-8 -*-
"""🛠 Admin buyrug'i - admin xohlagan foydalanuvchiga qo'lda pul yoki almaz yuboradi."""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    admin_credit_type_keyboard,
    gift_all_type_keyboard,
    gift_all_confirm_keyboard,
)

WAITING_CREDIT_AMOUNT, WAITING_CREDIT_USER_ID = range(30, 32)
WAITING_GIFT_AMOUNT = 33
WAITING_DEDUCT_USERNAME, WAITING_DEDUCT_AMOUNT = range(34, 36)


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


# ==================== 🎁 Hammaga sovg'a (barcha foydalanuvchilarga birdaniga) ====================

async def on_gift_all_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "🎁 <b>Hammaga sovg'a</b>\n\n"
        "Barcha foydalanuvchilarga BIRDANIGA nima yubormoqchisiz?",
        parse_mode="HTML",
        reply_markup=gift_all_type_keyboard(),
    )


async def on_gift_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    gift_type = query.data.split(":", 1)[1]  # "money" yoki "diamond"
    context.user_data["gift_type"] = gift_type

    label = "so'm (pul)" if gift_type == "money" else "dona almaz"
    await query.message.reply_text(
        f"💵 Har bir foydalanuvchiga qancha {label} yubormoqchisiz? (faqat raqam)\n\n"
        "Bekor qilish uchun /bekor."
    )
    return WAITING_GIFT_AMOUNT


async def receive_gift_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip().replace(" ", "")
    if not raw.isdigit() or int(raw) <= 0:
        await update.message.reply_text("⚠️ Noto'g'ri format. Faqat musbat raqam kiriting.")
        return WAITING_GIFT_AMOUNT

    amount = int(raw)
    context.user_data["gift_amount"] = amount
    gift_type = context.user_data.get("gift_type")
    label = "so'm" if gift_type == "money" else "dona almaz"

    user_ids = db.get_all_user_ids()
    await update.message.reply_text(
        f"⚠️ <b>Tasdiqlang</b>\n\n"
        f"Jami <b>{len(user_ids)}</b> ta foydalanuvchiga har biriga "
        f"<b>{amount} {label}</b> yuboriladi.\n\nDavom etasizmi?",
        parse_mode="HTML",
        reply_markup=gift_all_confirm_keyboard(),
    )
    return ConversationHandler.END


async def on_gift_all_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    await query.answer()

    gift_type = context.user_data.get("gift_type")
    amount = context.user_data.get("gift_amount")
    if not gift_type or not amount:
        await query.message.edit_text("⚠️ Xatolik yuz berdi. Qaytadan boshlang.")
        return

    label = "so'm" if gift_type == "money" else "dona almaz"
    user_ids = db.get_all_user_ids()

    await query.message.edit_text(f"⏳ Yuborilmoqda... (0/{len(user_ids)})")

    sent, failed = 0, 0
    for uid in user_ids:
        if gift_type == "money":
            db.add_balance(uid, amount)
        else:
            db.add_quiz_diamonds(uid, amount)

        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"🎉 Sizga <b>{amount} {label}</b> sovg'a qilindi!",
                parse_mode="HTML",
            )
            sent += 1
        except TelegramError:
            failed += 1
        await asyncio.sleep(0.05)

    await query.message.edit_text(
        f"✅ <b>Yakunlandi!</b>\n\n"
        f"💰 Har biriga: <b>{amount} {label}</b>\n"
        f"✅ Xabar yetkazildi: <b>{sent}</b> kishiga\n"
        f"❌ Yetkazilmadi: <b>{failed}</b> kishiga (hisobga baribir qo'shildi)",
        parse_mode="HTML",
    )
    context.user_data.pop("gift_type", None)
    context.user_data.pop("gift_amount", None)


async def on_gift_all_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("gift_type", None)
    context.user_data.pop("gift_amount", None)
    await query.message.edit_text("❌ Bekor qilindi.")


# ==================== ➖ Almazni ayirish (bitta a'zoning hisobidan) ====================

async def on_deduct_diamond_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    await update.message.reply_text(
        "➖ <b>Almazni ayirish</b>\n\n"
        "Qaysi a'zoning hisobidan almaz ayirmoqchisiz? Uning Telegram "
        "username'ini yuboring (masalan: <code>@ali_ff</code> yoki <code>ali_ff</code>).\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_DEDUCT_USERNAME


async def receive_deduct_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()
    if not raw:
        await update.message.reply_text(
            "⚠️ Iltimos, foydalanuvchining Telegram username'ini yuboring."
        )
        return WAITING_DEDUCT_USERNAME

    target = db.get_user_by_username(raw)
    if not target:
        await update.message.reply_text(
            f"⚠️ <b>@{raw.lstrip('@')}</b> username'li a'zo topilmadi. "
            "U bilan botdan foydalangan bo'lishi kerak.\n\n"
            "Qaytadan username yuboring yoki /bekor deb yozing.",
            parse_mode="HTML",
        )
        return WAITING_DEDUCT_USERNAME

    context.user_data["deduct_target_uid"] = target["user_id"]
    context.user_data["deduct_target_username"] = target["username"]
    context.user_data["deduct_target_first_name"] = target["first_name"]

    current_balance = db.get_quiz_diamonds(target["user_id"])
    await update.message.reply_text(
        f"👤 Topildi: {target['first_name'] or '-'} (@{target['username'] or '—'})\n"
        f"💎 Joriy almaz hisobi: <b>{current_balance}</b>\n\n"
        f"Hisobidan nechta almaz ayirmoqchisiz? (faqat raqam)\n\nBekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_DEDUCT_AMOUNT


async def receive_deduct_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip().replace(" ", "")
    if not raw.isdigit() or int(raw) <= 0:
        await update.message.reply_text("⚠️ Noto'g'ri format. Faqat musbat raqam kiriting.")
        return WAITING_DEDUCT_AMOUNT

    amount = int(raw)
    target_user_id = context.user_data.get("deduct_target_uid")
    target_username = context.user_data.get("deduct_target_username")
    target_first_name = context.user_data.get("deduct_target_first_name")

    if not target_user_id:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    deducted = db.deduct_quiz_diamonds(target_user_id, amount)
    remaining = db.get_quiz_diamonds(target_user_id)

    user_notify = f"⚠️ Hisobingizdan <b>{deducted}</b> dona almaz olib tashlandi."
    try:
        await context.bot.send_message(chat_id=target_user_id, text=user_notify, parse_mode="HTML")
        delivered = True
    except TelegramError:
        delivered = False

    status = (
        "✅ Foydalanuvchiga xabar yuborildi."
        if delivered
        else "⚠️ Foydalanuvchiga xabar yuborilmadi (botni bloklagan bo'lishi mumkin), "
        "lekin hisobidan baribir ayirildi."
    )
    await update.message.reply_text(
        f"✅ {target_first_name or '-'} (@{target_username or '—'}) hisobidan "
        f"<b>{deducted}</b> dona almaz ayirildi.\n"
        f"💎 Qolgan almaz: <b>{remaining}</b>\n\n{status}",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(True),
    )

    context.user_data.pop("deduct_target_uid", None)
    context.user_data.pop("deduct_target_username", None)
    context.user_data.pop("deduct_target_first_name", None)
    return ConversationHandler.END


async def cancel_deduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("deduct_target_uid", None)
    context.user_data.pop("deduct_target_username", None)
    context.user_data.pop("deduct_target_first_name", None)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True))
    return ConversationHandler.END
