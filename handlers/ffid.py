# -*- coding: utf-8 -*-
"""🎮 Mening FF ID'im - foydalanuvchi Free Fire ID yuborganda ma'lumot ko'rsatish."""

import httpx
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from config import FF_API_URL, FF_REGION
from keyboards import main_menu_keyboard

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

    await update.message.reply_text("⏳ Ma'lumotlar qidirilmoqda, biroz kuting...")

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.get(
                FF_API_URL, params={"region": FF_REGION, "uid": ff_id}
            )
            data = resp.json()
    except Exception:
        await update.message.reply_text(
            "❌ Ma'lumotlarni olishda xatolik yuz berdi. Server band bo'lishi "
            "mumkin, birozdan keyin qayta urinib ko'ring.",
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END

    if "error" in data or "basicInfo" not in data:
        await update.message.reply_text(
            "⚠️ Bunday UID topilmadi yoki noto'g'ri kiritildi. Iltimos, "
            "UID raqamini tekshirib qaytadan urinib ko'ring.",
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END

    basic = data.get("basicInfo", {})
    clan = data.get("clanBasicInfo", {})
    credit = data.get("creditScoreInfo", {})

    text = (
        "🎮 <b>Free Fire profil ma'lumotlari</b>\n\n"
        f"👤 Nickname: {basic.get('nickname', '—')}\n"
        f"🆔 UID: {basic.get('accountId', ff_id)}\n"
        f"🌍 Region: {basic.get('region', FF_REGION)}\n"
        f"📶 Level: {basic.get('level', '—')}\n"
        f"❤️ Likes: {basic.get('liked', '—')}\n"
        f"🏆 Rank: {basic.get('rank', '—')}\n"
        f"🎯 CS Rank: {basic.get('csRank', '—')}\n"
        f"🛡 Guild: {clan.get('clanName', '—')}\n"
        f"🆔 Guild ID: {clan.get('clanId', '—')}\n"
        f"⭐ Honor Score: {credit.get('creditScore', '—')}"
    )
    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END
