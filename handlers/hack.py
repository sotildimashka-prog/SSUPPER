# -*- coding: utf-8 -*-
"""🔫 Maxsus xizmat - Proxy server, Cheat va panellar hamda 🕹️ Mening FF ID'im
bittasi ostida jamlangan bo'lim (inline tugmalar, har birida orqaga tugmasi)."""

import asyncio
import httpx

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

import database as db
from config import ADMIN_ID, FF_API_URL, FF_REGION
from keyboards import main_menu_keyboard

DEFAULT_CHEAT_TEXT = "🔧 <b>Cheat va panellar</b>\n\nTez orada qo'shiladi."
DEFAULT_PROXY_TEXT = "🌐 <b>Proxy server</b>\n\nHozircha bo'sh."

HACK_MENU_TEXT = "🔫🔥 <b>Maxsus xizmat</b>\n\nKerakli bo'limni tanlang 👇"

WAITING_FF_ID = 40


def hack_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🛰️ Proxy server", callback_data="hack:proxy")],
            [InlineKeyboardButton("🛠️ Cheat va panellar", callback_data="hack:cheat")],
            [InlineKeyboardButton("🕹️ Mening FF ID'im", callback_data="hack:ffid")],
        ]
    )


def hack_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Orqaga", callback_data="hack:back")]]
    )


async def _send_stored(message, setting_key: str, default_text: str, reply_markup=None):
    text = db.get_setting(setting_key, default_text)
    await message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


# ==================== Asosiy menyu ====================

async def on_hack_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HACK_MENU_TEXT, parse_mode="HTML", reply_markup=hack_menu_keyboard()
    )


async def on_hack_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _send_stored(
        query.message, "proxy_text", DEFAULT_PROXY_TEXT, reply_markup=hack_back_keyboard()
    )


async def on_hack_cheat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _send_stored(
        query.message, "cheat_text", DEFAULT_CHEAT_TEXT, reply_markup=hack_back_keyboard()
    )


async def on_hack_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_text(
            HACK_MENU_TEXT, parse_mode="HTML", reply_markup=hack_menu_keyboard()
        )
    except Exception:
        await query.message.reply_text(
            HACK_MENU_TEXT, parse_mode="HTML", reply_markup=hack_menu_keyboard()
        )


# ==================== 🕹️ Mening FF ID'im (Maxsus xizmat ichida) ====================

async def on_hack_ffid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "🎮 <b>Mening FF ID'im</b>\n\n"
        "Iltimos, Free Fire UID (ID) raqamingizni yuboring.\n"
        "Bekor qilish uchun /bekor buyrug'ini yuboring.",
        parse_mode="HTML",
    )
    return WAITING_FF_ID


async def cancel_ffid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id == ADMIN_ID
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END


async def _fetch_ff_data(ff_id: str):
    """API'ga so'rov yuboradi. Server uxlab qolgan bo'lsa, 2 marta qayta urinadi."""
    last_error = None
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=75) as client:
                resp = await client.get(
                    FF_API_URL, params={"region": FF_REGION, "uid": ff_id}
                )
                return resp.json()
        except Exception as e:
            last_error = e
            await asyncio.sleep(3)
    raise last_error


async def receive_ff_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ff_id = (update.message.text or "").strip()
    is_admin = update.effective_user.id == ADMIN_ID

    if not ff_id.isdigit():
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Iltimos, faqat raqamlardan iborat Free Fire "
            "UID yuboring yoki /bekor bilan chiqing."
        )
        return WAITING_FF_ID

    await update.message.reply_text(
        "⏳ Ma'lumotlar qidirilmoqda...\n"
        "Server ba'zan uyg'onishi uchun 30-60 soniya vaqt olishi mumkin, iltimos kuting."
    )

    try:
        data = await _fetch_ff_data(ff_id)
    except Exception:
        await update.message.reply_text(
            "❌ Server hozircha javob bermayapti. Birozdan so'ng qaytadan "
            "urinib ko'ring (bepul server tez-tez band bo'lib turadi).",
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END

    if not isinstance(data, dict) or "error" in data or "basicInfo" not in data:
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
