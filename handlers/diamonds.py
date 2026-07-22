# -*- coding: utf-8 -*-
"""💎 Almaz sotib olish va 💰 Hisobim bo'limlari - to'liq xarid va to'lov oqimi."""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID, ADMIN_USERNAME, CARD_NUMBER, CARD_HOLDER_NAME, CARD_PHONE
from keyboards import (
    main_menu_keyboard,
    diamonds_entry_keyboard,
    diamonds_admin_keyboard,
    diamonds_packages_keyboard,
    package_detail_keyboard,
    insufficient_balance_keyboard,
    account_keyboard,
    account_admin_keyboard,
    paid_confirm_keyboard,
    admin_topup_review_keyboard,
    admin_order_review_keyboard,
)
from data.diamonds_data import find_package, detail_text

WAITING_ORDER_FF_ID = 10
WAITING_TOPUP_AMOUNT = 11
WAITING_TOPUP_RECEIPT = 12


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ==================== 💎 ALMAZ SOTIB OLISH ====================

async def on_diamonds_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 <b>Almaz sotib olish</b>\n\n"
        "Qanday yo'l bilan sotib olmoqchisiz?",
        parse_mode="HTML",
        reply_markup=diamonds_entry_keyboard(),
    )


async def on_diamonds_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "👤 Admin bilan bevosita bog'lanish uchun tugmani bosing 👇",
        reply_markup=diamonds_admin_keyboard(ADMIN_USERNAME),
    )


async def on_diamonds_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💎 <b>Almaz paketini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=diamonds_packages_keyboard(),
    )


async def on_diamonds_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💎 <b>Almaz sotib olish</b>\n\nQanday yo'l bilan sotib olmoqchisiz?",
        parse_mode="HTML",
        reply_markup=diamonds_entry_keyboard(),
    )


async def on_package_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    item = find_package(key)
    if not item:
        return
    await query.edit_message_text(
        detail_text(item),
        parse_mode="HTML",
        reply_markup=package_detail_keyboard(key),
    )


async def start_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    item = find_package(key)
    if not item:
        return ConversationHandler.END

    user_id = query.from_user.id
    price = item["price_som"]

    if not db.deduct_balance(user_id, price):
        await query.edit_message_text(
            "❌ <b>Hisobingizda mablag' yetarli emas.</b>\n\n"
            "Iltimos, 💰 <b>Hisobim</b> bo'limidan hisobingizni to'ldiring, "
            "so'ngra qaytadan urinib ko'ring.",
            parse_mode="HTML",
            reply_markup=insufficient_balance_keyboard(),
        )
        return ConversationHandler.END

    label = f"{item['diamonds']} 💎" if "label" not in item else f"{item['label']} ({item['diamonds']} 💎)"
    order_id = db.create_diamond_order(user_id, label, price)
    context.user_data["pending_order_id"] = order_id

    await query.edit_message_text(
        "✅ To'lov hisobingizdan yechildi!\n\n"
        "🆔 Endi Free Fire UID (ID) raqamingizni yuboring:",
    )
    return WAITING_ORDER_FF_ID


async def receive_order_ff_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ff_id = (update.message.text or "").strip()
    is_admin = _is_admin(update.effective_user.id)
    order_id = context.user_data.get("pending_order_id")

    if not order_id:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan /start bosing.",
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END

    if not ff_id.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Faqat raqamlardan iborat UID yuboring."
        )
        return WAITING_ORDER_FF_ID

    db.set_diamond_order_ff_id(order_id, ff_id)
    order = db.get_diamond_order(order_id)
    user = update.effective_user

    await update.message.reply_text(
        "⏳ <b>Almaz yo'lda, sabr qiling...</b>\n\n"
        "Admin tez orada hisobingizga almazlarni tashlaydi.",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "💎 <b>Yangi almaz buyurtmasi</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"📦 Paket: {order['package_label']}\n"
        f"💵 Narxi: {order['price']:,} so'm\n"
        f"🎮 Free Fire UID: <code>{ff_id}</code>\n\n"
        "Almazni tashlagach, pastdagi tugmani bosing 👇"
    ).replace(",", ".")

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=admin_order_review_keyboard(order_id),
        )
    except TelegramError:
        pass

    context.user_data.pop("pending_order_id", None)
    return ConversationHandler.END


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    order_id = context.user_data.pop("pending_order_id", None)
    if order_id:
        order = db.get_diamond_order(order_id)
        if order:
            db.add_balance(update.effective_user.id, order["price"])
        db.update_diamond_order_status(order_id, "cancelled")
    await update.message.reply_text(
        "❌ Bekor qilindi. Agar pul yechilgan bo'lsa, hisobingizga qaytarildi.",
        reply_markup=main_menu_keyboard(is_admin),
    )
    return ConversationHandler.END


async def order_sent_by_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin 'Yubordim' tugmasini bosganda."""
    query = update.callback_query
    if not _is_admin(query.from_user.id):
        await query.answer("Bu tugma faqat admin uchun.", show_alert=True)
        return
    await query.answer()

    order_id = int(query.data.split(":", 1)[1])
    order = db.get_diamond_order(order_id)
    if not order:
        return

    db.update_diamond_order_status(order_id, "delivered")

    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                "🎉 <b>Almaz tushdi!</b>\n\n"
                "✅ Buyurtmangiz muvaffaqiyatli yetkazib berildi.\n"
                "Ishonchingiz uchun rahmat! Xizmatimizdan foydalanganingiz uchun "
                "tashakkur. Salomat bo'ling 💎🔥"
            ),
            parse_mode="HTML",
        )
    except TelegramError:
        pass

    try:
        await query.edit_message_text(
            query.message.text + "\n\n✅ <b>Yetkazib berildi</b>", parse_mode="HTML"
        )
    except TelegramError:
        pass


async def go_to_account_hint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "👇 Pastdagi <b>💰 Hisobim</b> tugmasini bosing.", parse_mode="HTML"
    )


# ==================== 💰 HISOBIM ====================

async def on_account_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance = db.get_balance(update.effective_user.id)
    await update.message.reply_text(
        f"💰 <b>Hisobim</b>\n\n"
        f"💵 Joriy balans: <b>{balance:,} so'm</b>\n\n".replace(",", ".") +
        "Hisobingizni qanday to'ldirmoqchisiz?",
        parse_mode="HTML",
        reply_markup=account_keyboard(),
    )


async def on_account_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "👤 Admin bilan bevosita bog'lanish uchun tugmani bosing 👇",
        reply_markup=account_admin_keyboard(ADMIN_USERNAME),
    )


async def on_account_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "Assalomu aleykum, to'lov uchun karta raqami ⚡️\n\n"
        f"( Isim familiya {CARD_HOLDER_NAME} ) ⚡️ boshqa isim chiqsa to'lov qilmang\n\n"
        "cheksiz qabul yo'q, ulangan raqam: "
        f"{CARD_PHONE}\n\n"
        f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        "(ustiga bosangiz nusxa olinadi) 🎉\n\n"
        "To'lov qilib bo'lgach, pastdagi <b>✅ To'lov qildim</b> tugmasini bosing."
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=paid_confirm_keyboard())


async def start_topup_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("💵 Qancha to'lov qildingiz? (faqat raqam, so'mda)")
    return WAITING_TOPUP_AMOUNT


async def receive_topup_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip().replace(" ", "")
    if not raw.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Faqat raqam kiriting (masalan: 13000)."
        )
        return WAITING_TOPUP_AMOUNT

    context.user_data["pending_topup_amount"] = int(raw)
    await update.message.reply_text("📷 Endi to'lov chekining rasmini yuboring.")
    return WAITING_TOPUP_RECEIPT


async def receive_topup_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    amount = context.user_data.get("pending_topup_amount")

    if not update.message.photo:
        await update.message.reply_text("⚠️ Iltimos, chek rasmini (fotosurat) yuboring.")
        return WAITING_TOPUP_RECEIPT

    if not amount:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END

    photo_file_id = update.message.photo[-1].file_id
    user = update.effective_user
    request_id = db.create_topup_request(user.id, amount, photo_file_id)

    await update.message.reply_text(
        "⏳ <b>Sabr qiling, tekshiruvda...</b>",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )

    caption = (
        "💳 <b>Yangi to'lov cheki</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"💵 Bildirilgan summa: <b>{amount:,} so'm</b>".replace(",", ".")
    )
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=admin_topup_review_keyboard(request_id),
        )
    except TelegramError:
        pass

    context.user_data.pop("pending_topup_amount", None)
    return ConversationHandler.END


async def cancel_topup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    context.user_data.pop("pending_topup_amount", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END


async def topup_approved(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _is_admin(query.from_user.id):
        await query.answer("Bu tugma faqat admin uchun.", show_alert=True)
        return
    await query.answer()

    request_id = int(query.data.split(":", 1)[1])
    req = db.get_topup_request(request_id)
    if not req or req["status"] != "pending":
        return

    db.add_balance(req["user_id"], req["amount"])
    db.update_topup_status(request_id, "approved")

    try:
        await context.bot.send_message(
            chat_id=req["user_id"],
            text=(
                f"✅ <b>Hisobingiz {req['amount']:,} so'mga to'ldirildi!</b>\n\n"
                "Endi 💎 Almaz sotib olish bo'limidan xarid qilishingiz mumkin."
            ).replace(",", "."),
            parse_mode="HTML",
        )
    except TelegramError:
        pass

    try:
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ <b>Tasdiqlandi</b>", parse_mode="HTML"
        )
    except TelegramError:
        pass


async def topup_rejected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _is_admin(query.from_user.id):
        await query.answer("Bu tugma faqat admin uchun.", show_alert=True)
        return
    await query.answer()

    request_id = int(query.data.split(":", 1)[1])
    req = db.get_topup_request(request_id)
    if not req or req["status"] != "pending":
        return

    db.update_topup_status(request_id, "rejected")

    try:
        await context.bot.send_message(
            chat_id=req["user_id"],
            text="❌ <b>Soxta chek qabul qilinmadi.</b>\n\nIltimos, to'g'ri chek yuboring "
                 "yoki admin bilan bog'laning.",
            parse_mode="HTML",
        )
    except TelegramError:
        pass

    try:
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n❌ <b>Rad etildi</b>", parse_mode="HTML"
        )
    except TelegramError:
        pass
