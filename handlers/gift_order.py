# -*- coding: utf-8 -*-
"""🎁 Giftlar - o'yin ichidagi sovg'a (gift) xizmatlari: Character Gift,
Emote Gift, Gun Skin Gift, Evo Gun Gift, Bundle Gift.

Foydalanuvchi kerakli turni tanlaydi -> gift nomini yoki rasmini yuboradi ->
so'rov adminga inline tugma bilan boradi -> admin narxni to'g'ridan-to'g'ri
o'sha foydalanuvchiga yuboradi (📲 Shaxsiy nastroyka bo'limidagi kabi)."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    gift_order_keyboard,
    gift_order_item_back_keyboard,
    gift_order_admin_keyboard,
)

WAITING_GIFT_ORDER_ITEM = 91
WAITING_GIFT_ORDER_ADMIN_REPLY = 92

GIFT_ORDER_TEXT = (
    "🎁 <b>Giftlar</b>\n\n"
    "Bu bo'limda o'yin ichidagi sovg'a xizmatlari joylashgan.\n"
    "Kerakli turini tanlang 👇"
)

GIFT_TYPE_LABELS = {
    "character": "🎁 Character Gift",
    "emote": "🎁 Emote Gift",
    "gunskin": "🎁 Gun Skin Gift",
    "evogun": "🎁 Evo Gun Gift",
    "bundle": "🎁 Bundle Gift",
}


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def on_gift_order_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        GIFT_ORDER_TEXT, parse_mode="HTML", reply_markup=gift_order_keyboard()
    )


async def on_gift_order_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("gift_order_key", None)
    context.user_data.pop("gift_order_label", None)
    await query.edit_message_text(
        GIFT_ORDER_TEXT, parse_mode="HTML", reply_markup=gift_order_keyboard()
    )
    return ConversationHandler.END


async def on_gift_order_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    label = GIFT_TYPE_LABELS.get(key, "🎁 Gift")
    context.user_data["gift_order_key"] = key
    context.user_data["gift_order_label"] = label

    await query.edit_message_text(
        f"{label}\n\n"
        "Kerakli gift nomini yoki rasmini tashlang, biz narxini aytamiz.\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
        reply_markup=gift_order_item_back_keyboard(),
    )
    return WAITING_GIFT_ORDER_ITEM


async def receive_gift_order_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    label = context.user_data.get("gift_order_label", "🎁 Gift")
    msg = update.message
    user = update.effective_user

    if not (msg.text or msg.photo):
        await update.message.reply_text(
            "⚠️ Iltimos, gift nomini matn yoki rasm ko'rinishida yuboring."
        )
        return WAITING_GIFT_ORDER_ITEM

    await update.message.reply_text(
        "✅ So'rovingiz qabul qilindi!\n\nAdmin tez orada narxini aytadi.",
        reply_markup=main_menu_keyboard(is_admin),
    )

    caption = (
        f"🎁 <b>Yangi Gift so'rovi: {label}</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
    )

    try:
        if msg.photo:
            extra = f"\n📝 Izoh: {msg.caption}" if msg.caption else ""
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=msg.photo[-1].file_id,
                caption=caption + extra + "\n\nJavob (narx) yuborish uchun pastdagi tugmani bosing 👇",
                parse_mode="HTML",
                reply_markup=gift_order_admin_keyboard(user.id),
            )
        else:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=caption + f"\n📝 Matn: {msg.text}\n\n"
                "Javob (narx) yuborish uchun pastdagi tugmani bosing 👇",
                parse_mode="HTML",
                reply_markup=gift_order_admin_keyboard(user.id),
            )
    except TelegramError:
        pass

    context.user_data.pop("gift_order_key", None)
    context.user_data.pop("gift_order_label", None)
    return ConversationHandler.END


async def cancel_gift_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    context.user_data.pop("gift_order_key", None)
    context.user_data.pop("gift_order_label", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END


# ---------- Admin javobi (narxni yozib yuboradi: matn/rasm/video/hujjat) ----------

async def start_gift_order_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    target_user_id = int(query.data.split(":", 1)[1])
    context.user_data["gift_reply_target_uid"] = target_user_id

    await query.message.reply_text(
        "✍️ Ushbu foydalanuvchi uchun narxni (yoki javobni) yuboring "
        "(matn, rasm yoki video bo'lishi mumkin).\n\nBekor qilish uchun /bekor."
    )
    return WAITING_GIFT_ORDER_ADMIN_REPLY


async def cancel_gift_order_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("gift_reply_target_uid", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def receive_gift_order_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user_id = context.user_data.get("gift_reply_target_uid")
    if not target_user_id:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    msg = update.message
    caption_prefix = "🎁 <b>Gift bo'yicha javob:</b>\n\n"

    try:
        if msg.photo:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_photo(
                chat_id=target_user_id, photo=msg.photo[-1].file_id,
                caption=caption, parse_mode="HTML",
            )
        elif msg.video:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_video(
                chat_id=target_user_id, video=msg.video.file_id,
                caption=caption, parse_mode="HTML",
            )
        elif msg.document:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_document(
                chat_id=target_user_id, document=msg.document.file_id,
                caption=caption, parse_mode="HTML",
            )
        else:
            text = caption_prefix + (msg.text_html or msg.text or "")
            await context.bot.send_message(
                chat_id=target_user_id, text=text, parse_mode="HTML"
            )
        await update.message.reply_text(
            "✅ Foydalanuvchiga muvaffaqiyatli yuborildi!",
            reply_markup=main_menu_keyboard(True),
        )
    except TelegramError:
        await update.message.reply_text(
            "❌ Yuborishda xatolik yuz berdi (foydalanuvchi botni bloklagan bo'lishi mumkin).",
            reply_markup=main_menu_keyboard(True),
        )

    context.user_data.pop("gift_reply_target_uid", None)
    return ConversationHandler.END
