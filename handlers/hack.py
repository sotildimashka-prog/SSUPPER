# -*- coding: utf-8 -*-
"""🔓 Free Fire Hack - Proxy server, Cheat va panellar, Mening FF ID'im birlashtirilgan menyu."""

import asyncio
import httpx
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

import database as db
from config import FF_API_URL, FF_REGION, ADMIN_ID
from keyboards import hack_menu_keyboard, hack_back_keyboard, hack_content_keyboard, main_menu_keyboard

WAITING_FF_ID = 1

DEFAULT_CHEAT_TEXT = "🔧 <b>Cheat va panellar</b>\n\nTez orada qo'shiladi."
DEFAULT_PROXY_TEXT = "🌐 <b>Proxy server</b>\n\nHozircha bo'sh."


async def _send_content(query_or_msg, content: dict, back_markup, edit: bool):
    """Matn yoki media (rasm/video/fayl) ko'rsatadi."""
    ctype = content.get("type", "text")
    caption = content.get("caption") or content.get("text") or ""

    if ctype == "text" or not content.get("file_id"):
        if edit:
            await query_or_msg.edit_message_text(caption, parse_mode="HTML", reply_markup=back_markup)
        else:
            await query_or_msg.reply_text(caption, parse_mode="HTML", reply_markup=back_markup)
        return

    # Media bo'lsa - avval eski inline xabarni matn bilan almashtiramiz, keyin faylni yuboramiz
    if edit:
        try:
            await query_or_msg.edit_message_text("⏳ Yuklanmoqda...")
        except Exception:
            pass
        chat_id = query_or_msg.message.chat_id
        bot = query_or_msg.get_bot()
    else:
        chat_id = query_or_msg.chat_id
        bot = query_or_msg.get_bot()

    if ctype == "photo":
        await bot.send_photo(chat_id, content["file_id"], caption=caption, parse_mode="HTML", reply_markup=back_markup)
    elif ctype == "video":
        await bot.send_video(chat_id, content["file_id"], caption=caption, parse_mode="HTML", reply_markup=back_markup)
    elif ctype == "document":
        await bot.send_document(chat_id, content["file_id"], caption=caption, parse_mode="HTML", reply_markup=back_markup)
    else:
        await bot.send_message(chat_id, caption, parse_mode="HTML", reply_markup=back_markup)


async def on_hack_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔓 <b>Free Fire Hack</b>\n\nKerakli bo'limni tanlang 👇",
        parse_mode="HTML",
        reply_markup=hack_menu_keyboard(),
    )


async def on_hack_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔓 <b>Free Fire Hack</b>\n\nKerakli bo'limni tanlang 👇",
        parse_mode="HTML",
        reply_markup=hack_menu_keyboard(),
    )


async def on_hack_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    content = db.get_content("proxy_text", DEFAULT_PROXY_TEXT)
    await _send_content(query, content, hack_content_keyboard(), edit=True)


async def on_hack_cheat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    content = db.get_content("cheat_text", DEFAULT_CHEAT_TEXT)
    await _send_content(query, content, hack_content_keyboard(), edit=True)


# ---------- Mening FF ID'im (Hack menyusi ichida) ----------

async def on_hack_ffid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🕹️ <b>Mening FF ID'im</b>\n\n"
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
