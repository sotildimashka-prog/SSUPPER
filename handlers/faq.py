# -*- coding: utf-8 -*-
"""📬 Savollar (FAQ) - foydalanuvchi savol yozadi, admin javob beradi."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

from config import ADMIN_ID
from keyboards import faq_admin_keyboard

WAITING_FAQ_QUESTION, WAITING_FAQ_ADMIN_REPLY = range(2)

ASK_QUESTION_TEXT = (
    "📬 <b>Savol yuboring</b>\n\n"
    "Savolingizni yozib yuboring, tez orada admin javob beradi.\n\n"
    "Bekor qilish uchun /bekor yozing."
)


# ---------- Foydalanuvchi savol yuboradi ----------

async def start_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ASK_QUESTION_TEXT, parse_mode="HTML")
    return WAITING_FAQ_QUESTION


async def start_faq_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xizmatlar inline menyusidagi '📬 Savollar (FAQ)' tugmasi bosilganda ishlaydi."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(ASK_QUESTION_TEXT, parse_mode="HTML")
    return WAITING_FAQ_QUESTION


async def receive_faq_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    question = update.message.text

    text = (
        "📬 <b>Yangi savol!</b>\n\n"
        f"👤 Ism: {user.first_name or '-'}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🔗 Username: @{user.username if user.username else '—'}\n\n"
        f"❓ Savol: {question}"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            parse_mode="HTML",
            reply_markup=faq_admin_keyboard(user.id),
        )
    except TelegramError:
        pass

    await update.message.reply_text("✅ Savolingiz qabul qilindi! Tez orada javob beramiz.")
    return ConversationHandler.END


async def cancel_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END


# ---------- Admin javob beradi ----------

async def start_faq_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Bu tugma faqat admin uchun.", show_alert=True)
        return ConversationHandler.END

    target_user_id = int(query.data.split(":", 1)[1])
    context.user_data["faq_reply_target"] = target_user_id

    await query.message.reply_text(
        f"✍️ Foydalanuvchi (<code>{target_user_id}</code>) uchun javobingizni yozing.\n\n"
        "Bekor qilish uchun /bekor yozing.",
        parse_mode="HTML",
    )
    return WAITING_FAQ_ADMIN_REPLY


async def receive_faq_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user_id = context.user_data.get("faq_reply_target")
    if not target_user_id:
        await update.message.reply_text("⚠️ Xatolik: foydalanuvchi topilmadi.")
        return ConversationHandler.END

    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"📬 <b>Sizning savolingizga javob:</b>\n\n{update.message.text}",
            parse_mode="HTML",
        )
        await update.message.reply_text("✅ Javob foydalanuvchiga yuborildi.")
    except TelegramError:
        await update.message.reply_text(
            "❌ Xabar yuborilmadi (foydalanuvchi botni bloklagan bo'lishi mumkin)."
        )

    context.user_data.pop("faq_reply_target", None)
    return ConversationHandler.END


async def cancel_faq_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("faq_reply_target", None)
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END
