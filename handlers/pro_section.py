# -*- coding: utf-8 -*-
"""👑 Pro obuna FAOLLASHGANDAN KEYINGI maxsus bo'lim.

Faqat Pro obuna sotib olgan (database.is_pro_user) foydalanuvchilar uchun
ochiq bo'lgan qizil tugmali bo'lim:

  🇧🇷 Brazillian nastroyka -> telefon modeli so'raladi -> admin qo'lda
                              nastroyka tayyorlab yuboradi (mavjud
                              "customreply:" oqimi qayta ishlatiladi).
  ✨ Super nik            -> hech kimda yo'q, noyob Free Fire niklar ro'yxati
                              (SUPER_NICKNAMES) darhol ko'rsatiladi.
  🎁 Sirli sovg'a          -> "Admin sirli sovg'angizni tayyorlab qo'ydi,
                              unga yozing" matni + admin bilan bog'lanish
                              tugmasi.
  🏆 Mukofot               -> mavjud "Yutiqni chiqarish" (Pul/Almaz) oqimi.
  🎬 AI video yasash       -> prompt so'raladi -> admin qo'lda video
                              tayyorlab yuboradi ("video" order_kind).
  🖼️ AI rasm yasash        -> prompt so'raladi -> admin qo'lda rasm
                              tayyorlab yuboradi ("rasm" order_kind).
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    pro_sub_active_keyboard,
    pro_section_back_keyboard,
    pro_section_cancel_keyboard,
    pro_secret_gift_keyboard,
    custom_admin_keyboard,
    withdraw_win_type_keyboard,
)
from data.nicknames_data import SUPER_NICKNAMES

WAITING_PRO_BRAZIL_MODEL, WAITING_PRO_VIDEO_PROMPT, WAITING_PRO_RASM_PROMPT = range(3)

# 🎁 "Sirli sovg'a" bo'limi uchun maxsus admin lichkasi (aynan shu username
# ko'rsatilishi so'ralgan).
SECRET_GIFT_ADMIN_USERNAME = "freefireolmos"

PRO_WELCOME_TEXT = (
    "👑 <b>Yangi bo'limga xush kelibsiz!</b>\n\n"
    "Siz <b>PRO OBUNA</b> bo'limidasiz. 🎉\n\n"
    "Quyidagi maxsus imkoniyatlardan foydalanishingiz mumkin 👇"
)


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def _require_pro(query) -> bool:
    if not db.is_pro_user(query.from_user.id):
        await query.answer(
            "⛔️ Bu bo'lim faqat Pro obuna foydalanuvchilari uchun.", show_alert=True
        )
        return False
    return True


# ---------------------------------------------------------------------------
# ⬅️ Pro obuna bo'limiga qaytish
# ---------------------------------------------------------------------------
async def on_prosec_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_text(
            PRO_WELCOME_TEXT, parse_mode="HTML", reply_markup=pro_sub_active_keyboard()
        )
    except TelegramError:
        await query.message.reply_text(
            PRO_WELCOME_TEXT, parse_mode="HTML", reply_markup=pro_sub_active_keyboard()
        )
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# 🇧🇷 Brazillian nastroyka
# ---------------------------------------------------------------------------
async def on_prosec_brazilian(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not await _require_pro(query):
        return ConversationHandler.END
    await query.answer()
    await query.message.reply_text(
        "🇧🇷 <b>Brazillian nastroyka</b>\n\n"
        "Bu — Braziliyalik pro o'yinchilar uslubidagi maxsus, eksklyuziv "
        "nastroyka.\n\n"
        "📱 Telefon modelingizni to'liq va aniq yozing (brend + model), "
        "admin shu asosda sizga maxsus nastroykani tayyorlab yuboradi.\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
        reply_markup=pro_section_cancel_keyboard(),
    )
    return WAITING_PRO_BRAZIL_MODEL


async def cancel_pro_brazilian(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END


async def receive_pro_brazilian_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    model_text = (update.message.text or "").strip()
    if not model_text:
        await update.message.reply_text("⚠️ Iltimos, telefon modelini matn ko'rinishida yuboring.")
        return WAITING_PRO_BRAZIL_MODEL

    is_admin = _is_admin(user.id)
    await update.message.reply_text(
        "✅ So'rovingiz qabul qilindi!\n\n"
        "Admin tez orada sizga Brazillian nastroykani tayyorlab yuboradi.",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "🇧🇷 <b>Yangi BRAZILLIAN NASTROYKA buyurtmasi (Pro obuna)!</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"📱 Telefon modeli:\n{model_text}"
    )
    context.bot_data.setdefault("pending_orders", {})[user.id] = {
        "type_label": "🇧🇷 Brazillian nastroyka",
        "user_id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "info": f"📱 Telefon modeli: {model_text}",
    }
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=custom_admin_keyboard(
                user.id, "📤 Nastroyka yuborish", order_kind="brazilian"
            ),
        )
    except TelegramError:
        pass

    return ConversationHandler.END


# ---------------------------------------------------------------------------
# ✨ Super nik (hech kimda yo'q, noyob niklar)
# ---------------------------------------------------------------------------
async def on_prosec_superik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not await _require_pro(query):
        return
    await query.answer()

    lines = [f"<code>{n}</code>" for n in SUPER_NICKNAMES]
    text = (
        "✨ <b>Super nik</b>\n\n"
        "🔒 Bu niklar faqat Pro obunachilarga ko'rsatiladi va hech kimda yo'q!\n\n"
        + "\n".join(lines)
        + "\n\n👆 Ustiga bosib nusxa olishingiz mumkin."
    )
    try:
        await query.edit_message_text(
            text, parse_mode="HTML", reply_markup=pro_section_back_keyboard()
        )
    except TelegramError:
        await query.message.reply_text(
            text, parse_mode="HTML", reply_markup=pro_section_back_keyboard()
        )


# ---------------------------------------------------------------------------
# 🎁 Sirli sovg'a
# ---------------------------------------------------------------------------
async def on_prosec_sirli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not await _require_pro(query):
        return
    await query.answer()

    text = (
        "🎁 <b>Sirli sovg'a</b>\n\n"
        "Admin sirli sovg'angizni tayyorlab qo'ydi. Uni olish uchun "
        "adminga yozing 👇"
    )
    try:
        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=pro_secret_gift_keyboard(SECRET_GIFT_ADMIN_USERNAME),
        )
    except TelegramError:
        await query.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=pro_secret_gift_keyboard(SECRET_GIFT_ADMIN_USERNAME),
        )


# ---------------------------------------------------------------------------
# 🏆 Mukofot (Botta 1-o'rin mukofotini olish -> Yutiqni chiqarish oqimi)
# ---------------------------------------------------------------------------
async def on_prosec_mukofot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not await _require_pro(query):
        return
    await query.answer()

    text = (
        "🏆 <b>Mukofot</b>\n\n"
        "Botta 1-o'rin mukofotini yutiqni chiqarish orqali olishingiz mumkin. "
        "Nimani chiqarmoqchisiz? 👇"
    )
    try:
        await query.edit_message_text(
            text, parse_mode="HTML", reply_markup=withdraw_win_type_keyboard()
        )
    except TelegramError:
        await query.message.reply_text(
            text, parse_mode="HTML", reply_markup=withdraw_win_type_keyboard()
        )


# ---------------------------------------------------------------------------
# 🎬 AI video yasash (Pro)
# ---------------------------------------------------------------------------
async def on_prosec_aivideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not await _require_pro(query):
        return ConversationHandler.END
    await query.answer()
    await query.message.reply_text(
        "🎬 <b>AI video yasash</b>\n\n"
        "✍️ Video uchun promt yozing (nima haqida, qanday uslubda, kim/nima "
        "tasvirlanishi kerak - batafsil yozing).\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
        reply_markup=pro_section_cancel_keyboard(),
    )
    return WAITING_PRO_VIDEO_PROMPT


async def cancel_pro_aivideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END


async def receive_pro_video_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    prompt_text = (update.message.text or "").strip()
    if not prompt_text:
        await update.message.reply_text("⚠️ Iltimos, matn ko'rinishida yozing.")
        return WAITING_PRO_VIDEO_PROMPT

    is_admin = _is_admin(user.id)
    await update.message.reply_text(
        "✅ So'rovingiz qabul qilindi!\n\n🎬 Admin tez orada videongizni tayyorlab yuboradi.",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "🎬 <b>Yangi AI VIDEO YASASH buyurtmasi (Pro obuna)!</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"📝 Promt:\n{prompt_text}"
    )
    context.bot_data.setdefault("pending_orders", {})[user.id] = {
        "type_label": "🎬 AI video yasash (Pro)",
        "user_id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "info": f"📝 Promt: {prompt_text}",
    }
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=custom_admin_keyboard(user.id, "📤 Video yuborish", order_kind="video"),
        )
    except TelegramError:
        pass

    return ConversationHandler.END


# ---------------------------------------------------------------------------
# 🖼️ AI rasm yasash (Pro)
# ---------------------------------------------------------------------------
async def on_prosec_airasm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not await _require_pro(query):
        return ConversationHandler.END
    await query.answer()
    await query.message.reply_text(
        "🖼️ <b>AI rasm yasash</b>\n\n"
        "✍️ Rasm uchun promt yozing (nima haqida, qanday uslubda - batafsil "
        "yozing).\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
        reply_markup=pro_section_cancel_keyboard(),
    )
    return WAITING_PRO_RASM_PROMPT


async def cancel_pro_airasm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END


async def receive_pro_rasm_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    prompt_text = (update.message.text or "").strip()
    if not prompt_text:
        await update.message.reply_text("⚠️ Iltimos, matn ko'rinishida yozing.")
        return WAITING_PRO_RASM_PROMPT

    is_admin = _is_admin(user.id)
    await update.message.reply_text(
        "✅ So'rovingiz qabul qilindi!\n\n🖼️ Admin tez orada rasmingizni tayyorlab yuboradi.",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "🖼️ <b>Yangi AI RASM YASASH buyurtmasi (Pro obuna)!</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"📝 Promt:\n{prompt_text}"
    )
    context.bot_data.setdefault("pending_orders", {})[user.id] = {
        "type_label": "🖼️ AI rasm yasash (Pro)",
        "user_id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "info": f"📝 Promt: {prompt_text}",
    }
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=custom_admin_keyboard(user.id, "📤 Rasm yuborish", order_kind="rasm"),
        )
    except TelegramError:
        pass

    return ConversationHandler.END
