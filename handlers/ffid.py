# -*- coding: utf-8 -*-
"""🎮 Mening FF ID'im - foydalanuvchi Free Fire ID yuborganda ma'lumot ko'rsatish."""

import httpx
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from config import FF_API_URL, FF_API_KEY
from keyboards import main_menu_keyboard, BTN_FFID

WAITING_FF_ID = 1


async def start_ffid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 <b>Mening FF ID'im</b>\n\n"
        "Iltimos, Free Fire UID (ID) raqamingizni yuboring.\n"
        "Bekor qilish uchun /bekor buyrug'ini yuboring.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    return WAITING_FF_ID


async def cancel_ffid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import ADMIN_ID

    is_admin = update.effective_user.id == ADMIN_ID
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END


async def receive_ff_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import ADMIN_ID

    ff_id = (update.message.text or "").strip()
    is_admin = update.effective_user.id == ADMIN_ID

    if not ff_id.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Iltimos, faqat raqamlardan iborat Free Fire "
            "UID yuboring yoki /bekor bilan chiqing."
        )
        return WAITING_FF_ID

    if not FF_API_URL:
        await update.message.reply_text(
            "⚙️ Free Fire ID tekshirish xizmati hozircha ulanmagan.\n\n"
            "Admin FF_API_URL va FF_API_KEY sozlamalarini config.py yoki "
            "environment o'zgaruvchilarida to'ldirishi kerak. Buni qanday "
            "qilish README.md faylida tushuntirilgan.",
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END

    await update.message.reply_text("⏳ Ma'lumotlar qidirilmoqda...")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            headers = {"Authorization": f"Bearer {FF_API_KEY}"} if FF_API_KEY else {}
            resp = await client.get(f"{FF_API_URL}?uid={ff_id}", headers=headers)
            data = resp.json()
    except Exception:
        await update.message.reply_text(
            "❌ Ma'lumotlarni olishda xatolik yuz berdi. Keyinroq qayta urinib ko'ring.",
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END

    text = (
        "🎮 <b>Free Fire profil ma'lumotlari</b>\n\n"
        f"👤 Nickname: {data.get('nickname', '—')}\n"
        f"🆔 UID: {data.get('uid', ff_id)}\n"
        f"🌍 Region: {data.get('region', '—')}\n"
        f"📶 Level: {data.get('level', '—')}\n"
        f"❤️ Likes: {data.get('likes', '—')}\n"
        f"🏆 Rank: {data.get('rank', '—')}\n"
        f"🎯 CS Rank: {data.get('cs_rank', '—')}\n"
        f"🛡 Guild: {data.get('guild_name', '—')}\n"
        f"🆔 Guild ID: {data.get('guild_id', '—')}\n"
        f"⭐ Honor Score: {data.get('honor_score', '—')}"
    )
    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END
