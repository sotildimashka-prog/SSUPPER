# -*- coding: utf-8 -*-
"""📊 Statistika, 📣 Xabar yuborish, 🖋️ Post va ✏️ Tugmalarni tahrirlash - faqat admin uchun."""

import asyncio

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
)

WAITING_BROADCAST = 2
WAITING_POST_TEXT = 3
WAITING_POST_BUTTON = 4
WAITING_EDIT_TEXT = 5

WAITING_FFTOUR_CONTENT = 100
WAITING_FFTOUR_CHANNEL = 101
WAITING_FFACC_CONTENT = 102
WAITING_FFACC_LINK = 103

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
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"📅 Bugungi yangi foydalanuvchilar: <b>{stats['today_users']}</b>\n"
        f"📈 Bugungi /start bosishlar: <b>{stats['today_starts']}</b>\n"
        f"📨 Jami xabarlar soni: <b>{stats['total_messages']}</b>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


# ---------- 📣 Oddiy Xabar yuborish (Broadcast) ----------

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END
    await update.message.reply_text(
        "📣 Barcha foydalanuvchilarga yuboriladigan xabar matnini kiriting.\n"
        "Bekor qilish uchun /bekor.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return WAITING_BROADCAST


async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


# ---------- 🖋️ Post (tugmali xabar) ----------

async def start_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _admin_only(update):
        return ConversationHandler.END
    await update.message.reply_text(
        "🖋️ <b>Yangi post yaratish</b>\n\n"
        "Post matnini yuboring (rasm bilan ham bo'lishi mumkin, rasmga izoh "
        "sifatida matn yozing).\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    return WAITING_POST_TEXT


async def receive_post_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["post_message"] = update.message

    await update.message.reply_text(
        "🔘 <b>Tugma qo'shasizmi?</b>\n\n"
        "Agar post ostiga bosiladigan tugma qo'shmoqchi bo'lsangiz, quyidagi "
        "formatda yuboring:\n\n"
        "<code>Tugma matni | https://havola.com</code>\n\n"
        "Masalan:\n<code>Kanalga o'tish | https://t.me/kanal_nomi</code>\n\n"
        "Agar tugma kerak bo'lmasa, /otkazib_yuborish deb yozing.\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_POST_BUTTON


async def skip_post_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _broadcast_post(update, context, button=None)


async def receive_post_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()
    if "|" not in raw:
        await update.message.reply_text(
            "⚠️ Format noto'g'ri. Quyidagicha yuboring:\n\n"
            "<code>Tugma matni | https://havola.com</code>\n\n"
            "Yoki tugmasiz davom etish uchun /otkazib_yuborish yozing.",
            parse_mode="HTML",
        )
        return WAITING_POST_BUTTON

    label, url = [p.strip() for p in raw.split("|", 1)]
    if not url.startswith("http"):
        await update.message.reply_text(
            "⚠️ Havola http:// yoki https:// bilan boshlanishi kerak. Qaytadan "
            "urinib ko'ring yoki /otkazib_yuborish yozing."
        )
        return WAITING_POST_BUTTON

    button = InlineKeyboardMarkup([[InlineKeyboardButton(label, url=url)]])
    return await _broadcast_post(update, context, button=button)


async def cancel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("post_message", None)
    await update.message.reply_text(
        "❌ Post yaratish bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def _broadcast_post(update: Update, context: ContextTypes.DEFAULT_TYPE, button):
    original = context.user_data.pop("post_message", None)
    if original is None:
        await update.message.reply_text(
            "⚠️ Xatolik: post matni topilmadi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    user_ids = db.get_all_user_ids()
    await update.message.reply_text(
        f"⏳ Post {len(user_ids)} foydalanuvchiga yuborilmoqda..."
    )

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            if original.photo:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=original.photo[-1].file_id,
                    caption=original.caption or "",
                    parse_mode="HTML",
                    reply_markup=button,
                )
            else:
                await context.bot.send_message(
                    chat_id=uid,
                    text=original.text or "",
                    parse_mode="HTML",
                    reply_markup=button,
                )
            sent += 1
        except TelegramError:
            failed += 1
        await asyncio.sleep(0.05)

    await update.message.reply_text(
        f"✅ Post yuborildi!\n\n📨 Muvaffaqiyatli: {sent}\n❌ Xatolik: {failed}",
        reply_markup=main_menu_keyboard(True),
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
