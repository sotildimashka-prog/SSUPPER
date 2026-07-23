# -*- coding: utf-8 -*-
"""❓ Savol va Takliflar - foydalanuvchi murojaatini yozadi, adminga inline
tugma bilan boradi, admin javob bersa foydalanuvchiga to'g'ridan-to'g'ri
yetkaziladi."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

from config import ADMIN_ID
from keyboards import main_menu_keyboard, inquiry_admin_reply_keyboard

WAITING_FEEDBACK = 26
WAITING_FEEDBACK_ADMIN_REPLY = 27

PROMPT_TEXT = (
    "✍️ Murojaatingizni yozib qoldiring, tezroq javob berishga harakat qilamiz."
)


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def on_feedback_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(PROMPT_TEXT)
    return WAITING_FEEDBACK


async def receive_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("⚠️ Iltimos, murojaatingizni matn ko'rinishida yuboring.")
        return WAITING_FEEDBACK

    await update.message.reply_text(
        "✅ Murojaatingiz qabul qilindi! Tez orada javob beramiz.",
        reply_markup=main_menu_keyboard(is_admin),
    )

    user = update.effective_user
    admin_text = (
        "❓ <b>Savol va Taklif</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"📝 Matn:\n{text}\n\n"
        "Javob yuborish uchun pastdagi tugmani bosing 👇"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=inquiry_admin_reply_keyboard("feedback", user.id),
        )
    except TelegramError:
        pass
    return ConversationHandler.END


async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END


# ---------- Admin javobi ----------

async def start_feedback_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    _, _kind, target_user_id = query.data.split(":", 2)
    context.user_data["feedback_target_uid"] = int(target_user_id)

    await query.message.reply_text(
        "✍️ Ushbu foydalanuvchiga javobingizni yozing.\n\nBekor qilish uchun /bekor."
    )
    return WAITING_FEEDBACK_ADMIN_REPLY


async def cancel_feedback_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("feedback_target_uid", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def receive_feedback_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user_id = context.user_data.get("feedback_target_uid")
    if not target_user_id:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    text = "💬 <b>Sizning murojaatingizga javob:</b>\n\n" + (
        update.message.text_html or update.message.text or ""
    )
    try:
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

    context.user_data.pop("feedback_target_uid", None)
    return ConversationHandler.END
