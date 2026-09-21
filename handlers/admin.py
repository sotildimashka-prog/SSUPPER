# -*- coding: utf-8 -*-
"""📊 Statistika, 📣 Xabar yuborish, 📢 Majburiy obuna, 💎 Almaz yechish minimumi va ✏️ Tugmalarni tahrirlash - faqat admin uchun."""

import asyncio
import re

from telegram import (
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    edit_texts_keyboard,
    ff_admin_panel_keyboard,
    ffadmin_tour_actions_keyboard,
    ffadmin_acc_actions_keyboard,
    TOURNAMENT_SLOT_LABELS,
    nastroyka_admin_brands_keyboard,
    nastroyka_admin_models_keyboard,
    nastroyka_admin_type_keyboard,
    NASTROYKA_CONTENT_TYPES,
    turnirlar_list_keyboard,
    turnirlar_detail_keyboard,
    force_sub_admin_keyboard,
    broadcast_type_keyboard,
    broadcast_inline_button,
)
from data.settings_data import PHONES

WAITING_BROADCAST = 2
WAITING_EDIT_TEXT = 5

WAITING_BROADCAST_CHOICE = 112
WAITING_BROADCAST_INLINE_CONTENT = 113
WAITING_BROADCAST_BTN_TEXT = 114
WAITING_BROADCAST_BTN_URL = 115

WAITING_FFTOUR_CONTENT = 100
WAITING_FFTOUR_CHANNEL = 101
WAITING_FFACC_CONTENT = 102
WAITING_FFACC_LINK = 103

WAITING_NASTROYKA_CONTENT = 104

WAITING_TURNIR_DAY = 105
WAITING_TURNIR_TITLE = 106
WAITING_TURNIR_FORMAT = 107
WAITING_TURNIR_TIME = 108
WAITING_TURNIR_NOTE = 109

WAITING_FORCE_SUB_CHANNEL = 110
WAITING_MIN_WITHDRAW = 111

WAITING_ABOUT_USER = 120

TEXT_LABELS = {
    "help_text": "🎧 Yordam matni",
    "cheat_text": "🛠️ Cheat matni",
    "proxy_text": "🛰️ Proxy matni",
    "ff2017_content": "🎬 Free Fire 2017",
}


def _admin_only(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID


async def on_stats_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return
    stats = db.get_stats()
    ref_stats = db.get_referral_admin_stats()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"📅 Bugungi yangi foydalanuvchilar: <b>{stats['today_users']}</b>\n"
        f"📈 Bugungi /start bosishlar: <b>{stats['today_starts']}</b>\n"
        f"📨 Jami xabarlar soni: <b>{stats['total_messages']}</b>\n\n"
        "💎 <b>Almaz ishlash / Referal</b>\n"
        f"🔗 Jami referal havolalar: <b>{ref_stats['total_links']}</b>\n"
        f"👥 Tasdiqlangan (mukofotli) referallar: <b>{ref_stats['total_credited']}</b>\n"
        f"⏳ Jarima tekshiruvini kutayotganlar: <b>{ref_stats['pending_check']}</b>\n"
        f"⚠️ Qo'llangan jarimalar (taxminan): <b>{ref_stats['total_penalty_events']}</b>\n"
        f"💎 Foydalanuvchilardagi jami almazlar: <b>{ref_stats['total_diamonds']}</b>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


# ---------- 📣 Xabar yuborish (Broadcast) ----------

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END
    await update.message.reply_text(
        "📣 <b>Xabar yuborish turini tanlang:</b>\n\n"
        "📝 <b>Oddiy xabar</b> — barcha foydalanuvchilarga oddiy xabar yuboriladi.\n"
        "🟢 <b>Inline tugmali xabar</b> — xabar ostiga o'zingiz xohlagan nom va "
        "havolali (kanal/sahifa linki yoki shaxsiy - \"lichka\") yashil tugma "
        "qo'shib yuboriladi.",
        parse_mode="HTML",
        reply_markup=broadcast_type_keyboard(),
    )
    return WAITING_BROADCAST_CHOICE


async def on_broadcast_type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    choice = query.data.split(":", 1)[1]

    if choice == "cancel":
        try:
            await query.edit_message_text("❌ Bekor qilindi.")
        except TelegramError:
            pass
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="Asosiy menyu:",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    if choice == "simple":
        try:
            await query.edit_message_text(
                "📝 Barcha foydalanuvchilarga yuboriladigan xabar matnini "
                "(yoki rasm/video/faylni) kiriting.\nBekor qilish uchun /bekor."
            )
        except TelegramError:
            pass
        return WAITING_BROADCAST

    # choice == "inline"
    try:
        await query.edit_message_text(
            "🟢 Inline tugmali xabar uchun matn (yoki rasm/video/fayl) kiriting.\n"
            "Bekor qilish uchun /bekor."
        )
    except TelegramError:
        pass
    return WAITING_BROADCAST_INLINE_CONTENT


async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("broadcast_inline_message", None)
    context.user_data.pop("broadcast_btn_text", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END

    message = update.message
    user_ids = db.get_all_user_ids()

    await update.message.reply_text(
        f"⏳ Xabar {len(user_ids)} foydalanuvchiga yuborilmoqda..."
    )

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await context.bot.copy_message(
                chat_id=uid,
                from_chat_id=message.chat_id,
                message_id=message.message_id,
            )
            sent += 1
        except TelegramError:
            failed += 1
        await asyncio.sleep(0.05)

    await update.message.reply_text(
        f"✅ Xabar yuborildi!\n\n📨 Muvaffaqiyatli: {sent}\n❌ Xatolik: {failed}",
        reply_markup=main_menu_keyboard(True),
    )
    return ConversationHandler.END


# ---------- 🟢 Inline tugmali xabar (Broadcast + link tugma) ----------

async def receive_broadcast_inline_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END

    context.user_data["broadcast_inline_message"] = update.message
    await update.message.reply_text(
        "🔘 Endi tugma nomini kiriting (masalan: Kanalga o'tish, Admin bilan bog'lanish).\n"
        "Bekor qilish uchun /bekor.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return WAITING_BROADCAST_BTN_TEXT


async def receive_broadcast_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END

    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text(
            "⚠️ Tugma nomi bo'sh bo'lishi mumkin emas. Qaytadan kiriting yoki /bekor."
        )
        return WAITING_BROADCAST_BTN_TEXT

    context.user_data["broadcast_btn_text"] = text
    await update.message.reply_text(
        "🔗 Endi tugma uchun havolani kiriting:\n\n"
        "• Kanal/sahifa uchun: https://... yoki t.me/kanal_nomi\n"
        "• Shaxsiy xabar (lichka) uchun: @username yoki https://t.me/username\n\n"
        "Bekor qilish uchun /bekor."
    )
    return WAITING_BROADCAST_BTN_URL


def _normalize_broadcast_url(raw: str) -> str | None:
    """Foydalanuvchi kiritgan havolani (link yoki @username/lichka) to'g'ri
    URL formatiga keltiradi. Noto'g'ri bo'lsa None qaytaradi."""
    raw = (raw or "").strip()
    if not raw:
        return None
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    if raw.startswith("@"):
        return f"https://t.me/{raw[1:]}"
    if raw.startswith("t.me/"):
        return f"https://{raw}"
    # Faqat username yozilgan bo'lishi mumkin (lichka), masalan: shu_admin
    if re.fullmatch(r"[A-Za-z0-9_]{4,}", raw):
        return f"https://t.me/{raw}"
    return None


async def receive_broadcast_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END

    raw = (update.message.text or "").strip()
    url = _normalize_broadcast_url(raw)
    if not url:
        await update.message.reply_text(
            "⚠️ Havola noto'g'ri. https:// bilan boshlanadigan link, t.me/... "
            "yoki @username (lichka) ko'rinishida yuboring. Qaytadan urinib "
            "ko'ring yoki /bekor."
        )
        return WAITING_BROADCAST_BTN_URL

    message = context.user_data.get("broadcast_inline_message")
    btn_text = context.user_data.get("broadcast_btn_text") or "Batafsil"

    if message is None:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi, qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        context.user_data.pop("broadcast_inline_message", None)
        context.user_data.pop("broadcast_btn_text", None)
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup([[broadcast_inline_button(btn_text, url)]])
    user_ids = db.get_all_user_ids()

    await update.message.reply_text(
        f"⏳ Xabar {len(user_ids)} foydalanuvchiga yuborilmoqda..."
    )

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await context.bot.copy_message(
                chat_id=uid,
                from_chat_id=message.chat_id,
                message_id=message.message_id,
                reply_markup=keyboard,
            )
            sent += 1
        except TelegramError:
            failed += 1
        await asyncio.sleep(0.05)

    await update.message.reply_text(
        f"✅ Xabar yuborildi!\n\n📨 Muvaffaqiyatli: {sent}\n❌ Xatolik: {failed}",
        reply_markup=main_menu_keyboard(True),
    )

    context.user_data.pop("broadcast_inline_message", None)
    context.user_data.pop("broadcast_btn_text", None)
    return ConversationHandler.END


# ---------- 📢 Majburiy obuna - admin boshqaruvi ----------

def _force_sub_text() -> str:
    return (
        "📢 <b>Majburiy obuna kanallari</b>\n\n"
        "Foydalanuvchilar botdan foydalanishdan oldin quyidagi kanallarga "
        "obuna bo'lishi shart. Kanalni o'chirish uchun uning yonidagi "
        "🗑 tugmasini bosing, yangi kanal qo'shish uchun pastdagi "
        "\"➕ Kanal qo'shish\" tugmasini bosing."
    )


async def start_force_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return
    channels = db.get_required_channels()
    await update.message.reply_text(
        _force_sub_text(),
        parse_mode="HTML",
        reply_markup=force_sub_admin_keyboard(channels),
    )


async def on_force_sub_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    username = query.data.split(":", 2)[2]
    db.remove_required_channel(username)
    await query.answer("🗑 Kanal o'chirildi.")
    channels = db.get_required_channels()
    try:
        await query.edit_message_text(
            _force_sub_text(),
            parse_mode="HTML",
            reply_markup=force_sub_admin_keyboard(channels),
        )
    except TelegramError:
        pass


async def on_force_sub_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except TelegramError:
        pass


async def start_force_sub_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()
    try:
        await query.message.edit_text(
            "➕ <b>Yangi majburiy obuna kanali qo'shish</b>\n\n"
            "Kanal ma'lumotlarini quyidagi formatda yuboring:\n\n"
            "<code>Kanal nomi | username | emoji</code>\n\n"
            "Masalan:\n<code>Free Fire Yangiliklar | freefireyangiliklar | 🔥</code>\n\n"
            "Eslatma: bot shu kanalda ADMIN bo'lishi shart, aks holda obuna "
            "tekshiruvi ishlamaydi. Emoji ixtiyoriy - yozmasangiz ham bo'ladi:\n"
            "<code>Kanal nomi | username</code>\n\n"
            "Bekor qilish uchun /bekor.",
            parse_mode="HTML",
        )
    except TelegramError:
        pass
    return WAITING_FORCE_SUB_CHANNEL


async def receive_force_sub_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END

    raw = (update.message.text or "").strip()
    parts = [p.strip() for p in raw.split("|")]

    if len(parts) < 2 or not parts[0] or not parts[1]:
        await update.message.reply_text(
            "⚠️ Format noto'g'ri. Quyidagicha yuboring:\n\n"
            "<code>Kanal nomi | username | emoji</code>\n\n"
            "Yoki /bekor yozing.",
            parse_mode="HTML",
        )
        return WAITING_FORCE_SUB_CHANNEL

    name = parts[0]
    username = parts[1].lstrip("@").replace("https://t.me/", "").strip()
    emoji = parts[2] if len(parts) > 2 and parts[2] else "📡"

    if not username:
        await update.message.reply_text(
            "⚠️ Username noto'g'ri. Qaytadan urinib ko'ring yoki /bekor yozing."
        )
        return WAITING_FORCE_SUB_CHANNEL

    db.add_required_channel(name, username, emoji)

    await update.message.reply_text(
        f"✅ <b>{name}</b> (@{username}) majburiy obuna ro'yxatiga qo'shildi!",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(True),
    )

    channels = db.get_required_channels()
    await update.message.reply_text(
        _force_sub_text(),
        parse_mode="HTML",
        reply_markup=force_sub_admin_keyboard(channels),
    )
    return ConversationHandler.END


async def cancel_force_sub_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


# ---------- 💎 Almaz yechish minimumi - admin boshqaruvi ----------

async def start_min_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END
    current = db.get_min_withdraw()
    await update.message.reply_text(
        "💎 <b>Almaz yechish minimumi</b>\n\n"
        f"Hozirgi minimal miqdor: <b>{current}</b> dona almaz.\n\n"
        "Yangi minimal miqdorni raqam bilan yuboring (masalan: 200 yoki 400).\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    return WAITING_MIN_WITHDRAW


async def receive_min_withdraw_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()

    if not raw.isdigit() or int(raw) <= 0:
        await update.message.reply_text(
            "⚠️ Noto'g'ri format. Faqat musbat raqam kiriting (masalan: 200).\n"
            "Bekor qilish uchun /bekor."
        )
        return WAITING_MIN_WITHDRAW

    value = int(raw)
    db.set_min_withdraw(value)

    await update.message.reply_text(
        f"✅ Almaz yechish minimumi <b>{value}</b> ga o'zgartirildi!",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(True),
    )
    return ConversationHandler.END


async def cancel_min_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


# ---------- ✏️ Tugmalarni tahrirlash ----------

async def start_edit_texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return
    await update.message.reply_text(
        "✏️ <b>Qaysi matnni tahrirlaysiz?</b>",
        parse_mode="HTML",
        reply_markup=edit_texts_keyboard(),
    )


async def choose_text_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    key = query.data.split(":", 1)[1]
    context.user_data["editing_key"] = key
    label = TEXT_LABELS.get(key, key)

    content = db.get_content(key, "(hozircha standart matn ishlatilmoqda)")
    if content.get("type") == "text" or not content.get("file_id"):
        current = content.get("text", "")
    else:
        current = f"[{content['type'].upper()} fayl saqlangan] {content.get('caption', '')}"

    await query.edit_message_text(
        f"✏️ <b>{label}</b> uchun joriy holat:\n\n{current}\n\n"
        "Yangi matn, rasm, video yoki fayl yuboring (HTML teglar: &lt;b&gt;, &lt;i&gt; "
        "ishlatishingiz mumkin, rasm/video/fayl uchun izoh - caption - ham yozishingiz mumkin).\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_EDIT_TEXT


async def receive_new_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get("editing_key")
    if not key:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    message = update.message
    if message.photo:
        db.set_content(key, "photo", file_id=message.photo[-1].file_id, caption=message.caption or "")
    elif message.video:
        db.set_content(key, "video", file_id=message.video.file_id, caption=message.caption or "")
    elif message.document:
        db.set_content(key, "document", file_id=message.document.file_id, caption=message.caption or "")
    else:
        new_text = message.text_html or message.text or ""
        db.set_content(key, "text", text=new_text)

    context.user_data.pop("editing_key", None)

    label = TEXT_LABELS.get(key, key)
    await update.message.reply_text(
        f"✅ {label} muvaffaqiyatli yangilandi!",
        reply_markup=main_menu_keyboard(True),
    )
    return ConversationHandler.END


async def cancel_edit_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("editing_key", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


# ---------- 🗂 Turnir/Akkaunt boshqaruvi (faqat admin) ----------
# "Nima gap?" bo'limidagi Free Fire turnirlar (5 kun) va Free Fire
# akkauntlar shu yerdan qo'shiladi/tahrirlanadi/o'chiriladi.

def _normalize_link(raw: str) -> str:
    raw = (raw or "").strip()
    if raw.startswith("http"):
        return raw
    return f"https://t.me/{raw.lstrip('@')}"


def _ff_panel_text() -> str:
    return (
        "🗂 <b>Turnir va akkauntlar boshqaruvi</b>\n\n"
        "Quyidagi ro'yxatdan kerakli bo'limni tanlang.\n"
        "✅ — qo'shilgan, ❌ — hali qo'shilmagan."
    )


def _ff_panel_markup():
    status = db.get_all_tournament_status()
    acc_added = db.get_ff_account() is not None
    return ff_admin_panel_keyboard(status, acc_added)


async def on_ff_admin_panel_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return
    await update.message.reply_text(
        _ff_panel_text(), parse_mode="HTML", reply_markup=_ff_panel_markup()
    )


async def on_ff_admin_panel_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    await query.answer()
    try:
        await query.edit_message_text(
            _ff_panel_text(), parse_mode="HTML", reply_markup=_ff_panel_markup()
        )
    except TelegramError:
        pass


async def on_ff_admin_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except TelegramError:
        pass


async def on_ff_admin_tour_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    await query.answer()
    slot = query.data.split(":", 2)[2]
    label = TOURNAMENT_SLOT_LABELS.get(slot, slot)
    added = db.get_tournament(slot) is not None
    try:
        await query.edit_message_text(
            f"🏆 <b>{label}</b>\n\nKerakli amalni tanlang:",
            parse_mode="HTML",
            reply_markup=ffadmin_tour_actions_keyboard(slot, added),
        )
    except TelegramError:
        pass


async def on_ff_admin_tour_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()
    slot = query.data.split(":", 2)[2]
    context.user_data["fftour_slot"] = slot
    label = TOURNAMENT_SLOT_LABELS.get(slot, slot)
    await query.message.reply_text(
        f"➕ <b>{label}</b> uchun turnir ma'lumotini yuboring.\n\n"
        "Sana, vaqt va boshqa ma'lumotlarni matn qilib yozing (rasm bilan "
        "yuborsangiz, rasmga izoh sifatida yozing).\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_FFTOUR_CONTENT


async def receive_fftour_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.photo:
        context.user_data["fftour_content"] = {
            "type": "photo",
            "file_id": message.photo[-1].file_id,
            "caption": message.caption_html or message.caption or "",
        }
    else:
        context.user_data["fftour_content"] = {
            "type": "text",
            "file_id": "",
            "caption": message.text_html or message.text or "",
        }
    await update.message.reply_text(
        "📢 Endi turnir kanalini yuboring (masalan: <code>@kanal_nomi</code> "
        "yoki to'liq havola).\n\n"
        "Kanal kerak bo'lmasa /otkazib_yuborish deb yozing.\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_FFTOUR_CHANNEL


async def _save_fftour(update: Update, context: ContextTypes.DEFAULT_TYPE, channel_url: str):
    slot = context.user_data.pop("fftour_slot", None)
    content = context.user_data.pop("fftour_content", None)
    if not slot or not content:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    db.set_tournament(
        slot,
        content["type"],
        file_id=content.get("file_id", ""),
        caption=content.get("caption", ""),
        channel_url=channel_url,
    )
    label = TOURNAMENT_SLOT_LABELS.get(slot, slot)
    await update.message.reply_text(
        f"✅ {label} uchun turnir muvaffaqiyatli saqlandi!",
        reply_markup=main_menu_keyboard(True),
    )
    return ConversationHandler.END


async def skip_fftour_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _save_fftour(update, context, "")


async def receive_fftour_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = _normalize_link(update.message.text or "")
    return await _save_fftour(update, context, url)


async def cancel_fftour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("fftour_slot", None)
    context.user_data.pop("fftour_content", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def on_ff_admin_tour_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    slot = query.data.split(":", 2)[2]
    db.delete_tournament(slot)
    await query.answer("🗑 O'chirildi.")
    try:
        await query.edit_message_text(
            _ff_panel_text(), parse_mode="HTML", reply_markup=_ff_panel_markup()
        )
    except TelegramError:
        pass


async def on_ff_admin_acc_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    await query.answer()
    added = db.get_ff_account() is not None
    try:
        await query.edit_message_text(
            "🎮 <b>Free Fire akkaunt</b>\n\nKerakli amalni tanlang:",
            parse_mode="HTML",
            reply_markup=ffadmin_acc_actions_keyboard(added),
        )
    except TelegramError:
        pass


async def on_ff_admin_acc_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()
    await query.message.reply_text(
        "➕ Akkaunt haqida ma'lumot yuboring (rasm bilan yuborsangiz, "
        "rasmga izoh sifatida yozing).\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_FFACC_CONTENT


async def receive_ffacc_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.photo:
        context.user_data["ffacc_content"] = {
            "type": "photo",
            "file_id": message.photo[-1].file_id,
            "caption": message.caption_html or message.caption or "",
        }
    else:
        context.user_data["ffacc_content"] = {
            "type": "text",
            "file_id": "",
            "caption": message.text_html or message.text or "",
        }
    await update.message.reply_text(
        "🛒 Endi sotib olish uchun havolani yuboring (masalan: "
        "<code>https://t.me/auwsn</code>).\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_FFACC_LINK


async def receive_ffacc_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()
    if not raw:
        await update.message.reply_text(
            "⚠️ Havola bo'sh bo'lmasin. Qaytadan yuboring yoki /bekor."
        )
        return WAITING_FFACC_LINK
    buy_url = _normalize_link(raw)

    content = context.user_data.pop("ffacc_content", None)
    if not content:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    db.set_ff_account(
        content["type"],
        file_id=content.get("file_id", ""),
        caption=content.get("caption", ""),
        buy_url=buy_url,
    )
    await update.message.reply_text(
        "✅ Akkaunt muvaffaqiyatli saqlandi!", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def cancel_ffacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("ffacc_content", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def on_ff_admin_acc_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    db.delete_ff_account()
    await query.answer("🗑 O'chirildi.")
    try:
        await query.edit_message_text(
            _ff_panel_text(), parse_mode="HTML", reply_markup=_ff_panel_markup()
        )
    except TelegramError:
        pass


# ---------- 🏆 Free Fire Turnirlar (ochiq ro'yxat) - qo'shish / o'chirish, faqat admin ----------
# Bu "🏆 Free Fire Turnirlar" pastki tugmasi ostida ko'rinadigan, admin
# xohlagancha (bir kunda 3-4 tasi bo'lsa ham) turnir qo'shishi mumkin bo'lgan
# bo'lim. Foydalanuvchi tomoni handlers/turnirlar.py faylida.

from handlers.turnirlar import _list_caption  # noqa: E402


async def on_turniradmin_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()
    context.user_data["turnir_new"] = {}
    await query.message.reply_text(
        "🗓 Yangi turnir uchun <b>kunini</b> kiriting (masalan: "
        "<i>13-Sentabr, Shanba</i> yoki <i>Bugun</i>, <i>Ertaga</i>):\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_TURNIR_DAY


async def receive_turnir_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("turnir_new", {})["day_label"] = (update.message.text or "").strip()
    await update.message.reply_text(
        "🏷 Endi turnir <b>nomini</b> kiriting (masalan: <i>Free Fire Cup #1</i>):\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_TURNIR_TITLE


async def receive_turnir_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("turnir_new", {})["title"] = (update.message.text or "").strip()
    await update.message.reply_text(
        "⚔️ Endi turnir <b>formatini</b> kiriting "
        "(masalan: <i>3/3 Skvad</i>, <i>2/2 Duo</i>, <i>1/1 Solo</i>):\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_TURNIR_FORMAT


async def receive_turnir_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("turnir_new", {})["format_text"] = (update.message.text or "").strip()
    await update.message.reply_text(
        "🕐 Endi turnir <b>boshlanish vaqtini</b> kiriting (masalan: "
        "<i>19:00</i>):\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_TURNIR_TIME


async def receive_turnir_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("turnir_new", {})["time_text"] = (update.message.text or "").strip()
    await update.message.reply_text(
        "🎁 Sovrina jamg'armasi yoki qo'shimcha izoh kiriting.\n\n"
        "Kerak bo'lmasa /otkazib_yuborish deb yozing.\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_TURNIR_NOTE


async def _save_new_turnir(update: Update, context: ContextTypes.DEFAULT_TYPE, note: str):
    data = context.user_data.pop("turnir_new", None)
    if not data:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    db.add_turnir(
        day_label=data.get("day_label", ""),
        title=data.get("title", ""),
        format_text=data.get("format_text", ""),
        time_text=data.get("time_text", ""),
        note=note,
    )
    await update.message.reply_text(
        "✅ Yangi turnir muvaffaqiyatli qo'shildi va foydalanuvchilarga "
        "\"🏆 Free Fire Turnirlar\" bo'limida ko'rinadi!",
        reply_markup=main_menu_keyboard(True),
    )
    return ConversationHandler.END


async def skip_turnir_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _save_new_turnir(update, context, "")


async def receive_turnir_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    note = (update.message.text or "").strip()
    return await _save_new_turnir(update, context, note)


async def cancel_turnir_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("turnir_new", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def on_turniradmin_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    turnir_id = int(query.data.split(":", 2)[2])
    db.delete_turnir_by_id(turnir_id)
    await query.answer("🗑 Turnir o'chirildi.")

    turnirlar = db.get_turnirlar_list()
    caption = _list_caption(turnirlar)
    kb = turnirlar_list_keyboard(turnirlar, True)
    try:
        await query.edit_message_caption(caption=caption, parse_mode="HTML", reply_markup=kb)
    except TelegramError:
        try:
            await query.edit_message_text(text=caption, parse_mode="HTML", reply_markup=kb)
        except TelegramError:
            pass


# ---------- ➕ Nastroyka qo'shish (telefon modellariga kontent, faqat admin) ----------
# Oqim: brend tanlash -> model tanlash -> kontent turini tanlash
# (TEXT / RASM / VIDEO / TEXT+RASM / VIDEO+TEXT) -> admin ma'lumotni
# yuboradi -> shu telefon modeliga saqlanadi (database.set_nastroyka_content).

NASTROYKA_TYPE_LABELS = dict(NASTROYKA_CONTENT_TYPES)

NASTROYKA_TYPE_PROMPTS = {
    "text": "📝 Endi shu model uchun matnni yuboring.",
    "photo": "🖼 Endi shu model uchun rasmni yuboring (izohsiz).",
    "video": "🎬 Endi shu model uchun videoni yuboring (izohsiz).",
    "phototext": (
        "📦 Endi shu model uchun rasmni yuboring va matnni rasmga izoh "
        "(caption) qilib yozing."
    ),
    "videotext": (
        "🎬 Endi shu model uchun videoni yuboring va matnni videoga izoh "
        "(caption) qilib yozing."
    ),
}


async def on_nastroyka_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return
    await update.message.reply_text(
        "👑 <b>Nastroyka qo'shish</b>\n\nTelefon brendini tanlang 👇",
        parse_mode="HTML",
        reply_markup=nastroyka_admin_brands_keyboard(),
    )


async def on_nastroyka_admin_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except TelegramError:
        pass


async def on_nastroyka_admin_brand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    await query.answer()
    brand = query.data.split(":", 2)[2]
    if brand not in PHONES:
        return
    context.user_data["nastroyka_brand"] = brand
    try:
        await query.edit_message_text(
            f"👑 <b>{brand}</b>\n\nModelni tanlang 👇\n"
            "✅ — kontent qo'shilgan, ❌ — hali qo'shilmagan.",
            parse_mode="HTML",
            reply_markup=nastroyka_admin_models_keyboard(brand),
        )
    except TelegramError:
        pass


async def on_nastroyka_admin_back_brands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    await query.answer()
    try:
        await query.edit_message_text(
            "👑 <b>Nastroyka qo'shish</b>\n\nTelefon brendini tanlang 👇",
            parse_mode="HTML",
            reply_markup=nastroyka_admin_brands_keyboard(),
        )
    except TelegramError:
        pass


async def on_nastroyka_admin_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    await query.answer()
    model_name = query.data.split(":", 2)[2]
    context.user_data["nastroyka_model"] = model_name
    has_content = db.get_nastroyka_content(model_name) is not None
    status = "✅ Kontent mavjud." if has_content else "❌ Hali kontent qo'shilmagan."
    try:
        await query.edit_message_text(
            f"📱 <b>{model_name}</b>\n\n{status}\n\nKontent turini tanlang 👇",
            parse_mode="HTML",
            reply_markup=nastroyka_admin_type_keyboard(model_name, has_content),
        )
    except TelegramError:
        pass


async def on_nastroyka_admin_back_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    await query.answer()
    brand = context.user_data.get("nastroyka_brand")
    if not brand or brand not in PHONES:
        try:
            await query.edit_message_text(
                "👑 <b>Nastroyka qo'shish</b>\n\nTelefon brendini tanlang 👇",
                parse_mode="HTML",
                reply_markup=nastroyka_admin_brands_keyboard(),
            )
        except TelegramError:
            pass
        return
    try:
        await query.edit_message_text(
            f"👑 <b>{brand}</b>\n\nModelni tanlang 👇\n"
            "✅ — kontent qo'shilgan, ❌ — hali qo'shilmagan.",
            parse_mode="HTML",
            reply_markup=nastroyka_admin_models_keyboard(brand),
        )
    except TelegramError:
        pass


async def on_nastroyka_admin_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return
    model_name = context.user_data.get("nastroyka_model")
    if not model_name:
        await query.answer()
        return
    db.delete_nastroyka_content(model_name)
    await query.answer("🗑 O'chirildi.")
    try:
        await query.edit_message_text(
            f"📱 <b>{model_name}</b>\n\n❌ Hali kontent qo'shilmagan.\n\n"
            "Kontent turini tanlang 👇",
            parse_mode="HTML",
            reply_markup=nastroyka_admin_type_keyboard(model_name, False),
        )
    except TelegramError:
        pass


async def on_nastroyka_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _admin_only(update):
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()
    type_key = query.data.split(":", 2)[2]
    model_name = context.user_data.get("nastroyka_model")
    if not model_name or type_key not in NASTROYKA_TYPE_PROMPTS:
        return ConversationHandler.END
    context.user_data["nastroyka_type"] = type_key
    label = NASTROYKA_TYPE_LABELS.get(type_key, type_key)
    await query.message.reply_text(
        f"👑 <b>{model_name}</b> — {label}\n\n"
        f"{NASTROYKA_TYPE_PROMPTS[type_key]}\n\nBekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_NASTROYKA_CONTENT


async def receive_nastroyka_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END

    message = update.message
    model_name = context.user_data.get("nastroyka_model")
    type_key = context.user_data.get("nastroyka_type")
    if not model_name or not type_key:
        await message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    if type_key == "text":
        if not message.text:
            await message.reply_text("📝 Iltimos, matn yuboring.")
            return WAITING_NASTROYKA_CONTENT
        db.set_nastroyka_content(
            model_name, "text", text=message.text_html or message.text
        )
    elif type_key == "photo":
        if not message.photo:
            await message.reply_text("🖼 Iltimos, rasm yuboring.")
            return WAITING_NASTROYKA_CONTENT
        db.set_nastroyka_content(
            model_name, "photo", file_id=message.photo[-1].file_id
        )
    elif type_key == "video":
        if not message.video:
            await message.reply_text("🎬 Iltimos, video yuboring.")
            return WAITING_NASTROYKA_CONTENT
        db.set_nastroyka_content(
            model_name, "video", file_id=message.video.file_id
        )
    elif type_key == "phototext":
        if not message.photo:
            await message.reply_text("📦 Iltimos, rasm yuboring (matnni izoh qilib yozing).")
            return WAITING_NASTROYKA_CONTENT
        db.set_nastroyka_content(
            model_name,
            "photo",
            file_id=message.photo[-1].file_id,
            caption=message.caption_html or message.caption or "",
        )
    elif type_key == "videotext":
        if not message.video:
            await message.reply_text("🎬 Iltimos, video yuboring (matnni izoh qilib yozing).")
            return WAITING_NASTROYKA_CONTENT
        db.set_nastroyka_content(
            model_name,
            "video",
            file_id=message.video.file_id,
            caption=message.caption_html or message.caption or "",
        )
    else:
        return ConversationHandler.END

    context.user_data.pop("nastroyka_type", None)
    await message.reply_text(
        f"✅ <b>{model_name}</b> uchun nastroyka muvaffaqiyatli saqlandi!",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(True),
    )
    return ConversationHandler.END


async def cancel_nastroyka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("nastroyka_type", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


# ---------- ℹ️ Foydalanuvchi haqida (admin xohlagan foydalanuvchining
# to'liq ma'lumotini: /start bosgan sanasi, almazi, puli va h.k. ko'rish) ----------

async def on_about_user_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END
    await update.message.reply_text(
        "ℹ️ <b>Foydalanuvchi haqida ma'lumot</b>\n\n"
        "Foydalanuvchining USER (username) yoki Telegram ID sini yuboring:\n\n"
        "Masalan: <code>@ali_ff</code> yoki <code>123456789</code>\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_ABOUT_USER


async def receive_about_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END

    raw = (update.message.text or "").strip()
    row = db.resolve_user(raw)

    if row:
        target_id = row["user_id"]
        first_name = row["first_name"]
        username = row["username"]
        joined = row["joined_at"]
    else:
        uid = db.parse_user_id(raw)
        if not uid:
            await update.message.reply_text(
                "⚠️ Bunday foydalanuvchi topilmadi. Username (masalan "
                "<code>@ali_ff</code>) yoki Telegram ID (masalan "
                "<code>123456789</code>) yuboring.",
                parse_mode="HTML",
            )
            return WAITING_ABOUT_USER
        target_id, first_name, username, joined = uid, None, None, None

    balance = db.get_balance(target_id)
    diamonds = db.get_quiz_diamonds(target_id)
    ref_count = db.count_referrals(target_id)
    ref_links = db.count_referral_links(target_id)
    blocked_row = db.get_blocked_user(target_id)
    is_blocked = bool(blocked_row and blocked_row["is_active"])

    joined_text = joined[:10] if joined else "— (hali /start bosmagan)"
    username_text = f"@{username}" if username else "—"
    status_text = "🚫 Bloklangan" if is_blocked else "✅ Faol"

    text = (
        "ℹ️ <b>Foydalanuvchi haqida</b>\n\n"
        f"👤 Ism: {first_name or '—'}\n"
        f"🔗 Username: {username_text}\n"
        f"🆔 Telegram ID: <code>{target_id}</code>\n"
        f"📅 /start bosgan sana: {joined_text}\n"
        f"📌 Holati: {status_text}\n\n"
        f"💎 Almaz: {diamonds:,} dona\n"
        f"💰 Balans: {balance:,} so'm\n\n"
        f"👥 Tasdiqlangan referallar: {ref_count}\n"
        f"🔗 Jami referal havolalar: {ref_links}"
    ).replace(",", ".")

    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def cancel_about_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END
