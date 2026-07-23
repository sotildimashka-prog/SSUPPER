# -*- coding: utf-8 -*-
"""🎛️ Alohida nastroyka - foydalanuvchi telefon modelini batafsil yozib yuboradi,
so'rov adminga inline tugma bilan boradi, admin javobni yuborsa foydalanuvchiga
to'g'ridan-to'g'ri yetkaziladi."""

from telegram import (
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

from config import ADMIN_ID
from keyboards import main_menu_keyboard

WAITING_CUSTOM_REQUEST = 20
WAITING_CUSTOM_ADMIN_REPLY = 21


def _admin_reply_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("✍️ Nastroyka yuborish", callback_data=f"customreply:{user_id}")]]
    )


async def start_custom_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎛️✨ <b>Alohida nastroyka</b>\n\n"
        "Telefon modelingizni <b>to'liq va aniq</b> yozib yuboring "
        "(brend, model, agar bilsangiz RAM/protsessor kabi tafsilotlar bilan).\n\n"
        "Masalan: <i>Samsung Galaxy A54, 8GB RAM, Exynos 1380</i>\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    return WAITING_CUSTOM_REQUEST


async def cancel_custom_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id == ADMIN_ID
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END


async def receive_custom_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_admin = user.id == ADMIN_ID
    model_text = (update.message.text or "").strip()

    if not model_text:
        await update.message.reply_text(
            "⚠️ Iltimos, telefon modelingizni matn ko'rinishida yuboring."
        )
        return WAITING_CUSTOM_REQUEST

    await update.message.reply_text(
        "✅ So'rovingiz qabul qilindi!\n\n"
        "Admin tez orada telefoningiz uchun individual nastroykani tayyorlab, "
        "shu yerga yuboradi. Iltimos, kuting.",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "🎛️ <b>Yangi alohida nastroyka so'rovi</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"📱 Telefon modeli:\n{model_text}\n\n"
        "Ushbu foydalanuvchiga individual nastroyka yuborish uchun pastdagi "
        "tugmani bosing 👇"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=_admin_reply_keyboard(user.id),
        )
    except TelegramError:
        pass

    return ConversationHandler.END


# ---------- Admin javobi (matn, rasm yoki video bo'lishi mumkin) ----------

async def start_custom_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    target_user_id = int(query.data.split(":", 1)[1])
    context.user_data["custom_target_uid"] = target_user_id

    await query.message.reply_text(
        "✍️ Ushbu foydalanuvchi uchun nastroykani yuboring "
        "(matn, rasm yoki video bo'lishi mumkin).\n\nBekor qilish uchun /bekor."
    )
    return WAITING_CUSTOM_ADMIN_REPLY


async def cancel_custom_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("custom_target_uid", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def receive_custom_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user_id = context.user_data.get("custom_target_uid")
    if not target_user_id:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    msg = update.message
    caption_prefix = "🎯 <b>Sizning individual nastroykangiz tayyor!</b>\n\n"

    try:
        if msg.photo:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_photo(
                chat_id=target_user_id,
                photo=msg.photo[-1].file_id,
                caption=caption,
                parse_mode="HTML",
            )
        elif msg.video:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_video(
                chat_id=target_user_id,
                video=msg.video.file_id,
                caption=caption,
                parse_mode="HTML",
            )
        elif msg.document:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_document(
                chat_id=target_user_id,
                document=msg.document.file_id,
                caption=caption,
                parse_mode="HTML",
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

    context.user_data.pop("custom_target_uid", None)
    return ConversationHandler.END
