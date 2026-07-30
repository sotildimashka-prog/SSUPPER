# -*- coding: utf-8 -*-
"""🖼️ Rasm Yasash bo'limi.

🔥 Oddiy Rasm: foydalanuvchi nom/matn yozadi -> 10 ta uslubdan birini
   tanlaydi -> bot avtomatik tayyor natijani yuboradi (PIL orqali generatsiya).

💎 Maxsus Rasm: foydalanuvchi nom va tavsif yozadi -> buyurtma adminga
   yuboriladi, admin qo'lda tayyor rasmni yuborib javob beradi (mavjud
   "customreply:" oqimi qayta ishlatiladi).
"""

import os

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    rasm_menu_keyboard,
    oddiy_rasm_cancel_keyboard,
    oddiy_rasm_styles_keyboard,
    oddiy_rasm_result_keyboard,
    custom_admin_keyboard,
)
from data.rasm_uslublari_data import get_style
from handlers.subscription import require_subscription
import imagegen

(
    WAITING_ODDIY_TEXT,
    WAITING_MAXSUS_NAME,
    WAITING_MAXSUS_DESC,
) = range(3)


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ---------------------------------------------------------------------------
# Kirish nuqtasi
# ---------------------------------------------------------------------------
async def on_rasm_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_subscription(update, context):
        return
    await update.message.reply_text(
        "🖼️ <b>Rasm Yasash</b>\n\nQuyidagilardan birini tanlang 👇",
        parse_mode="HTML",
        reply_markup=rasm_menu_keyboard(),
    )


async def on_rasm_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("oddiy_rasm_text", None)
    try:
        await query.edit_message_text(
            "🖼️ <b>Rasm Yasash</b>\n\nQuyidagilardan birini tanlang 👇",
            parse_mode="HTML",
            reply_markup=rasm_menu_keyboard(),
        )
    except TelegramError:
        pass
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# 🔥 Oddiy Rasm
# ---------------------------------------------------------------------------
async def on_oddiy_rasm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_text(
            "🔥 <b>Oddiy Rasm</b>\n\n"
            "✍️ Rasm uchun nom yoki matn yozing (masalan: <i>ISM</i> yoki qisqa "
            "prompt).\n\nBekor qilish uchun /bekor.",
            parse_mode="HTML",
            reply_markup=oddiy_rasm_cancel_keyboard(),
        )
    except TelegramError:
        pass
    return WAITING_ODDIY_TEXT


async def cancel_oddiy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("oddiy_rasm_text", None)
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END


async def receive_oddiy_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("⚠️ Iltimos, matn ko'rinishida yozing.")
        return WAITING_ODDIY_TEXT

    context.user_data["oddiy_rasm_text"] = text

    grid_path = None
    try:
        grid_path = imagegen.generate_style_grid()
        with open(grid_path, "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption="🎨 <b>Qaysi rasmni tanlaysiz?</b>\n\nYuqoridagi rasmga qarab, raqamiga mos tugmani bosing 👇",
                parse_mode="HTML",
                reply_markup=oddiy_rasm_styles_keyboard(),
            )
    except Exception:
        await update.message.reply_text(
            "🎨 <b>Qaysi rasmni tanlaysiz?</b>\n\nYuqoridagi rasmga qarab, raqamiga mos tugmani bosing 👇",
            parse_mode="HTML",
            reply_markup=oddiy_rasm_styles_keyboard(),
        )
    finally:
        if grid_path and os.path.exists(grid_path):
            try:
                os.remove(grid_path)
            except OSError:
                pass

    return ConversationHandler.END


async def on_oddiy_style_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Tayyorlanmoqda...")

    style_id = query.data.split(":", 1)[1]
    text = context.user_data.get("oddiy_rasm_text")

    if not text:
        await query.answer("⚠️ Avval matn kiriting. Qaytadan boshlang.", show_alert=True)
        return

    style = get_style(style_id)
    result_path = None
    try:
        result_path = imagegen.generate_oddiy_rasm(text, style_id)
        with open(result_path, "rb") as f:
            await query.message.reply_photo(
                photo=f,
                caption=(
                    "✅ <b>Tayyor natija!</b>\n\n"
                    f"🎨 Uslub: {style['title'] if style else style_id}\n"
                    f"✍️ Matn: {text}"
                ),
                parse_mode="HTML",
                reply_markup=oddiy_rasm_result_keyboard(),
            )
    except Exception:
        await query.message.reply_text(
            "❌ Rasm yaratishda xatolik yuz berdi. Qaytadan urinib ko'ring."
        )
    finally:
        if result_path and os.path.exists(result_path):
            try:
                os.remove(result_path)
            except OSError:
                pass

    context.user_data.pop("oddiy_rasm_text", None)


# ---------------------------------------------------------------------------
# 💎 Maxsus Rasm
# ---------------------------------------------------------------------------
async def on_maxsus_rasm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_text(
            "💎 <b>Maxsus Rasm</b>\n\n"
            "✍️ Avval rasm uchun <b>nomni</b> yozing.\n\nBekor qilish uchun /bekor.",
            parse_mode="HTML",
            reply_markup=oddiy_rasm_cancel_keyboard(),
        )
    except TelegramError:
        pass
    return WAITING_MAXSUS_NAME


async def cancel_maxsus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("maxsus_rasm_name", None)
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END


async def receive_maxsus_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = (update.message.text or "").strip()
    if not name:
        await update.message.reply_text("⚠️ Iltimos, nomni matn ko'rinishida yozing.")
        return WAITING_MAXSUS_NAME

    context.user_data["maxsus_rasm_name"] = name
    await update.message.reply_text(
        "📝 Endi rasm uchun <b>tavsifni</b> (nima xohlaysiz, batafsil) yozing.\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_MAXSUS_DESC


async def receive_maxsus_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    desc = (update.message.text or "").strip()
    if not desc:
        await update.message.reply_text("⚠️ Iltimos, tavsifni matn ko'rinishida yozing.")
        return WAITING_MAXSUS_DESC

    name = context.user_data.pop("maxsus_rasm_name", "-")
    is_admin = _is_admin(user.id)

    await update.message.reply_text(
        "✅ Buyurtmangiz qabul qilindi!\n\n"
        "Admin tez orada sizning maxsus rasmingizni tayyorlab yuboradi.",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "💎 <b>Yangi MAXSUS RASM buyurtmasi!</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"🏷 Nom: {name}\n"
        f"📝 Tavsif:\n{desc}"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=custom_admin_keyboard(user.id),
        )
    except TelegramError:
        pass

    return ConversationHandler.END
