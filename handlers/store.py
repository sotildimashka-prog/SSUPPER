# -*- coding: utf-8 -*-
"""🛒 Free Fire Do'koni - Xaftalik/Oylik vaucher, Booyah Pass, Level Up Pass.

Xarid oqimi 💎 Almaz sotib olish bo'limidagi mavjud oqim bilan bir xil
mantiqda ishlaydi: balansdan pul yechiladi -> Free Fire UID so'raladi ->
so'rov adminga boradi -> admin "✅ Yubordim" tugmasini bosgach foydalanuvchiga
xabar boradi.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    store_menu_keyboard,
    store_item_detail_keyboard,
    store_admin_review_keyboard,
    insufficient_balance_keyboard,
)
from data.store_data import find_store_item

WAITING_STORE_FF_ID = 90

STORE_TEXT = (
    "🛒 <b>Free Fire Do'koni</b>\n\n"
    "Kerakli mahsulotni tanlang 👇"
)


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def _item_detail_text(item: dict) -> str:
    return (
        f"{item['label']}\n\n"
        f"📄 {item['desc']}\n\n"
        f"💵 Narxi: <b>{item['price']:,} so'm</b>".replace(",", ".")
    )


async def on_store_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        STORE_TEXT, parse_mode="HTML", reply_markup=store_menu_keyboard()
    )


async def on_store_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        STORE_TEXT, parse_mode="HTML", reply_markup=store_menu_keyboard()
    )


async def on_store_item_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    item = find_store_item(key)
    if not item:
        return
    await query.edit_message_text(
        _item_detail_text(item),
        parse_mode="HTML",
        reply_markup=store_item_detail_keyboard(key),
    )


async def start_store_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    item = find_store_item(key)
    if not item:
        return ConversationHandler.END

    user_id = query.from_user.id
    price = item["price"]

    if not db.deduct_balance(user_id, price):
        await query.edit_message_text(
            "❌ <b>Hisobingizda mablag' yetarli emas.</b>\n\n"
            "Iltimos, 💰 <b>Hisobim</b> bo'limidan hisobingizni to'ldiring, "
            "so'ngra qaytadan urinib ko'ring.",
            parse_mode="HTML",
            reply_markup=insufficient_balance_keyboard(),
        )
        return ConversationHandler.END

    order_id = db.create_diamond_order(user_id, item["label"], price)
    context.user_data["pending_store_order_id"] = order_id

    await query.edit_message_text(
        "✅ To'lov hisobingizdan yechildi!\n\n"
        "🆔 Endi Free Fire UID (ID) raqamingizni yuboring:",
    )
    return WAITING_STORE_FF_ID


async def receive_store_ff_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ff_id = (update.message.text or "").strip()
    is_admin = _is_admin(update.effective_user.id)
    order_id = context.user_data.get("pending_store_order_id")

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
        return WAITING_STORE_FF_ID

    db.set_diamond_order_ff_id(order_id, ff_id)
    order = db.get_diamond_order(order_id)
    user = update.effective_user

    await update.message.reply_text(
        "⏳ <b>Buyurtmangiz qabul qilindi, sabr qiling...</b>\n\n"
        "Admin tez orada hisobingizga tashlaydi.",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "🛒 <b>Yangi Free Fire Do'koni buyurtmasi</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"📦 Mahsulot: {order['package_label']}\n"
        f"💵 Narxi: {order['price']:,} so'm\n"
        f"🎮 Free Fire UID: <code>{ff_id}</code>\n\n"
        "Yuborgach, pastdagi tugmani bosing 👇"
    ).replace(",", ".")

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=store_admin_review_keyboard(order_id),
        )
    except TelegramError:
        pass

    context.user_data.pop("pending_store_order_id", None)
    return ConversationHandler.END


async def cancel_store_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    order_id = context.user_data.pop("pending_store_order_id", None)
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


async def store_order_sent_by_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin '✅ Yubordim' tugmasini bosganda."""
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
                "🎉 <b>Buyurtmangiz yetkazib berildi!</b>\n\n"
                f"✅ {order['package_label']} hisobingizga muvaffaqiyatli o'tkazildi.\n"
                "Xizmatimizdan foydalanganingiz uchun rahmat! 🔥"
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
