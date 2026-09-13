# -*- coding: utf-8 -*-
"""💘 Headshot Pro - pullik (VIP) nastroyka sotib olish oqimi.

Bosqichlar:
1) Salomlashuv + pullik nastroyka haqida umumiy ma'lumot (⬅️ Orqaga / Keyingisi ➡️)
2) Narxlar va kafolat haqida matn (⬅️ Orqaga / 🛒 Sotib olaman)
3) To'lov usulini tanlash: 🏧 Bankomat orqali yoki 💳 Humo/Uzcard orqali
4) Tanlangan usul bo'yicha karta ma'lumotlari + ✅ Bajarildi tugmasi
5) "Qancha to'lov qildingiz?" - foydalanuvchi summani yozadi
6) "Chek rasmini yoki videosini yuboring" - foydalanuvchi rasm/video yuboradi
7) Admin'ga to'lov ma'lumoti + chek yuboriladi, admin ✅/❌ orqali qaror qiladi
8) Foydalanuvchiga natija xabar qilinadi
"""

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes, ConversationHandler

import database as db
from handlers.message_utils import safe_edit_message
from config import ADMIN_ID, CARD_HOLDER_NAME, CARD_PHONE, HSPRO_CARD_NUMBER
from keyboards import (
    hspro_intro_keyboard,
    hspro_prices_keyboard,
    hspro_payment_method_keyboard,
    hspro_card_keyboard,
    hspro_amount_nav_keyboard,
    admin_hspro_review_keyboard,
    hspro_get_settings_keyboard,
    start_inline_keyboard,
)

WAITING_HSPRO_AMOUNT = 501
WAITING_HSPRO_RECEIPT = 502
WAITING_HSPRO_PHONE_MODEL = 503

METHOD_LABELS = {
    "atm": "🏧 Bankomat orqali",
    "humo": "💳 Humo/Uzcard orqali",
}

HSPRO_INTRO_TEXT = (
    "🤝 <b>Assalomu alaykum!</b>\n\n"
    "💘 <b>Headshot Pro</b> - bu sizning qo'lingizga mos, maxsus sozlangan "
    "PRO nastroyka bo'lib, headshot foizingizni sezilarli darajada oshiradi.\n\n"
    "✨ Pullik (PRO) nastroykani sotib olishning qulay tomonlari:\n"
    "🎯 Shaxsan sizning qo'lingizga moslab tayyorlanadi\n"
    "🔥 Yuqori headshot va aim aniqligi\n"
    "⚡️ Tezkor va silliq gameplay, kam recoil\n"
    "👑 Bepul nastroykalarga qaraganda ancha kuchliroq natija\n"
    "🛠 Muammo bo'lsa - admin bilan bevosita yordam\n\n"
    "Davom etish uchun pastdagi <b>Keyingisi ➡️</b> tugmasini bosing 👇"
)

HSPRO_PRICES_TEXT = (
    "💰 <b>Headshot Pro narxlari</b>\n\n"
    "🛡 Biz nastroykaga <b>kafolat</b> beramiz: agar sizda bot (avto-aim) "
    "bo'lmasa ham, nastroykaning o'zi natijani sezilarli oshiradi.\n\n"
    "📊 Headshot foizi bo'yicha narxlar:\n"
    "🔸 80% gacha - <b>20 000 so'm</b>\n"
    "🔸 90% gacha - <b>40 000 so'm</b>\n\n"
    "⚠️ Diqqat: <b>hech qachon 100% lik nastroyka bo'lmaydi</b> - buni "
    "va'da qiladigan har qanday joy aldoqchidir.\n\n"
    "Sotib olishni xohlasangiz, pastdagi tugmani bosing 👇"
)

PAYMENT_METHOD_TEXT = (
    "💳 <b>To'lov usulini tanlang</b>\n\nQuyidagilardan birini tanlang 👇"
)


async def on_hspro_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query, HSPRO_INTRO_TEXT, parse_mode="HTML", reply_markup=hspro_intro_keyboard()
    )


async def on_hspro_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query, HSPRO_PRICES_TEXT, parse_mode="HTML", reply_markup=hspro_prices_keyboard()
    )


async def on_hspro_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit_message(
        query, PAYMENT_METHOD_TEXT, parse_mode="HTML", reply_markup=hspro_payment_method_keyboard()
    )


def _card_text(method: str) -> str:
    header = "Assalomu aleykum, to'lov uchun karta ma'lumotlari ⚡️\n\n"
    holder_line = f"( Isim familiya {CARD_HOLDER_NAME} ) ⚡️ boshqa isim chiqsa to'lov qilmang\n\n"
    phone_line = f"cheksiz qabul yo'q, ulangan raqam: {CARD_PHONE}\n\n"

    if method == "atm":
        card_line = f"💳 Karta raqami: <code>{HSPRO_CARD_NUMBER}</code>\n(ustiga bosangiz nusxa olinadi) 🎉\n\n"
    else:
        # Humo/Uzcard: MUHIM - foydalanuvchi so'rovi bo'yicha bu yerda
        # karta raqami KO'RSATILMAYDI (hali tayyor emas / admin orqali beriladi).
        card_line = "💳 Karta raqami admin orqali yuboriladi, quyidagi tugma orqali davom eting.\n\n"

    footer = "To'lov qilib bo'lgach, pastdagi <b>✅ Bajarildi</b> tugmasini bosing."
    return header + holder_line + phone_line + card_line + footer


async def on_hspro_pay_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = query.data.split(":", 2)[2]
    context.user_data["hspro_method"] = method
    await safe_edit_message(
        query, _card_text(method), parse_mode="HTML", reply_markup=hspro_card_keyboard(method)
    )


async def on_hspro_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = query.data.split(":", 2)[2]
    context.user_data["hspro_method"] = method
    await safe_edit_message(
        query,
        "💰 Qancha to'lov qildingiz? (faqat raqam, so'mda)",
        reply_markup=hspro_amount_nav_keyboard(),
    )
    return WAITING_HSPRO_AMOUNT


async def receive_hspro_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip().replace(" ", "")
    if not raw.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Faqat raqam kiriting (masalan: 20000).",
            reply_markup=hspro_amount_nav_keyboard(),
        )
        return WAITING_HSPRO_AMOUNT

    context.user_data["hspro_amount"] = int(raw)
    await update.message.reply_text(
        f"✅ Sizning to'lovingiz <b>{int(raw):,} so'm</b> deb qabul qilindi.".replace(",", ".") +
        "\n\n📸 Endi chek rasmini yoki videosini yuboring."
        ,
        parse_mode="HTML",
    )
    return WAITING_HSPRO_RECEIPT


async def receive_hspro_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = context.user_data.get("hspro_amount")
    method = context.user_data.get("hspro_method", "atm")

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "photo"
    elif update.message.video:
        file_id = update.message.video.file_id
        file_type = "video"
    else:
        await update.message.reply_text("⚠️ Iltimos, chek rasmi yoki videosini yuboring.")
        return WAITING_HSPRO_RECEIPT

    if not amount:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=start_inline_keyboard(),
        )
        return ConversationHandler.END

    user = update.effective_user
    order_id = db.create_hspro_order(user.id, method, amount, file_id, file_type)

    await update.message.reply_text(
        "⏳ <b>Tekshirilmoqda, sabr qiling...</b>", parse_mode="HTML",
    )

    caption = (
        "💘 <b>Yangi Headshot Pro to'lovi</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"💳 Usul: {METHOD_LABELS.get(method, method)}\n"
        f"💵 Bildirilgan summa: <b>{amount:,} so'm</b>".replace(",", ".")
    )

    try:
        if file_type == "photo":
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=admin_hspro_review_keyboard(order_id),
            )
        else:
            await context.bot.send_video(
                chat_id=ADMIN_ID,
                video=file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=admin_hspro_review_keyboard(order_id),
            )
    except TelegramError:
        pass

    context.user_data.pop("hspro_amount", None)
    context.user_data.pop("hspro_method", None)
    return ConversationHandler.END


async def cancel_hspro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("hspro_amount", None)
    context.user_data.pop("hspro_method", None)

    query = update.callback_query
    if query is not None:
        await query.answer()
        await safe_edit_message(
            query, PAYMENT_METHOD_TEXT, parse_mode="HTML", reply_markup=hspro_payment_method_keyboard()
        )
    else:
        await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END


async def hspro_approved(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu tugma faqat admin uchun.", show_alert=True)
        return
    await query.answer()

    order_id = int(query.data.split(":", 1)[1])
    order = db.get_hspro_order(order_id)
    if not order or order["status"] != "pending":
        return

    db.update_hspro_order_status(order_id, "approved")

    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                "🎉 <b>To'lovingiz qabul qilindi!</b>\n\n"
                "💘 Headshot Pro nastroykangiz tez orada admin tomonidan "
                "shaxsiy chatga yuboriladi.\n\n"
                "👇 Nastroykangizni olish uchun pastdagi tugmani bosing."
            ),
            parse_mode="HTML",
            reply_markup=hspro_get_settings_keyboard(order_id),
        )
    except TelegramError:
        pass

    try:
        if query.message.caption:
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n✅ <b>Qabul qilindi</b>", parse_mode="HTML"
            )
    except TelegramError:
        pass


async def hspro_rejected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu tugma faqat admin uchun.", show_alert=True)
        return
    await query.answer()

    order_id = int(query.data.split(":", 1)[1])
    order = db.get_hspro_order(order_id)
    if not order or order["status"] != "pending":
        return

    db.update_hspro_order_status(order_id, "rejected")

    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                "❌ <b>To'lovingiz qabul qilinmadi.</b>\n\n"
                "Iltimos, to'g'ri chek yuboring yoki admin bilan bog'laning."
            ),
            parse_mode="HTML",
        )
    except TelegramError:
        pass

    try:
        if query.message.caption:
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ <b>Rad etildi</b>", parse_mode="HTML"
            )
    except TelegramError:
        pass


async def on_hspro_get_settings_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"🔧 Nastroykani olish" tugmasi bosilganda - telefon modelini so'raydi."""
    query = update.callback_query

    order_id = int(query.data.split(":", 1)[1])
    order = db.get_hspro_order(order_id)

    if not order or order["status"] != "approved":
        await query.answer("⚠️ Bu buyurtma topilmadi yoki hali tasdiqlanmagan.", show_alert=True)
        return ConversationHandler.END

    if query.from_user.id != order["user_id"]:
        await query.answer("Bu tugma faqat shu buyurtma egasi uchun.", show_alert=True)
        return ConversationHandler.END

    await query.answer()
    context.user_data["hspro_getset_order_id"] = order_id

    await query.message.reply_text(
        "📱 Telefon modelingizni kiriting (masalan: <code>iPhone 13</code> "
        "yoki <code>Samsung A54</code>):",
        parse_mode="HTML",
    )
    return WAITING_HSPRO_PHONE_MODEL


async def receive_hspro_phone_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_model = (update.message.text or "").strip()
    if not phone_model:
        await update.message.reply_text("⚠️ Iltimos, telefon modelini matn ko'rinishida yuboring.")
        return WAITING_HSPRO_PHONE_MODEL

    order_id = context.user_data.get("hspro_getset_order_id")
    order = db.get_hspro_order(order_id) if order_id else None

    if not order:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=start_inline_keyboard(),
        )
        context.user_data.pop("hspro_getset_order_id", None)
        return ConversationHandler.END

    user = update.effective_user
    db.save_hspro_phone_model(order_id, user.id, phone_model)

    await update.message.reply_text(
        "✅ <b>Nastroykangiz hozir tayyor!</b>\n\n"
        "🛠 Admin tez orada shaxsiy chatga nastroykani yuboradi.",
        parse_mode="HTML",
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🔧 <b>Nastroykani olish so'rovi</b>\n\n"
                f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
                f"🆔 Telegram ID: <code>{user.id}</code>\n"
                f"🧾 Buyurtma: #{order_id}\n"
                f"📱 Telefon modeli: <b>{phone_model}</b>"
            ),
            parse_mode="HTML",
        )
    except TelegramError:
        pass

    context.user_data.pop("hspro_getset_order_id", None)
    return ConversationHandler.END


async def cancel_hspro_get_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("hspro_getset_order_id", None)
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END


async def on_almaz_ishlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💎 Almaz ishlash - hozircha tayyor emas, keyinroq to'ldiriladi."""
    query = update.callback_query
    await query.answer(
        "🚧 Bu bo'lim tez orada qo'shiladi!", show_alert=True
    )
