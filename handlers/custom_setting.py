# -*- coding: utf-8 -*-
"""📲 Shaxsiy nastroyka - Pullik nastroyka (80%/97% Headshot, balansdan pul
yechiladi), Bepul nastroyka va Savollar bo'limlari. Har birida foydalanuvchi
telefon modelini (yoki savolini) yozadi, so'rov adminga inline tugma bilan
boradi, admin javobni (matn/rasm/video/hujjat) yuborsa foydalanuvchiga
to'g'ridan-to'g'ri yetkaziladi."""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

from config import ADMIN_ID, CUSTOM_SETTING_PRICES, CUSTOM_SETTING_STICKER_ID
from keyboards import (
    main_menu_keyboard,
    custom_entry_keyboard,
    custom_back_keyboard,
    custom_tiers_keyboard,
    custom_tier_detail_keyboard,
    custom_agree_keyboard,
    custom_admin_reply_keyboard,
    insufficient_balance_keyboard,
)
import database as db

WAITING_FREE_MODEL = 22
WAITING_PAID_MODEL = 23
WAITING_CUSTOM_QUESTION = 24
WAITING_CUSTOM_ADMIN_REPLY = 25

ENTRY_TEXT = (
    "📲✨ <b>Shaxsiy nastroyka</b>\n\n"
    "Quyidagilardan birini tanlang 👇"
)

DISCLAIMER_TEXT = (
    "⚠️ ILTIMOS, OXIRIGACHA DIQQAT BILAN O'QING!\n\n"
    "📌 Muhim eslatma:\n"
    "🎯 Hech qanday nastroyka 100% Headshot bermaydi.\n"
    "❌ Shu sababli biz \"100% Headshot Nastroyka\" deb reklama qilmaymiz va "
    "bunday xizmatni sotmaymiz.\n"
    "✅ Biz faqat quyidagi ekranda ko'rsatilgan Premium Nastroykalarni taqdim etamiz.\n\n"
    "📱 Har bir telefonning:\n"
    "• Modeli\n"
    "• Protsessori\n"
    "• Ekrani\n"
    "• FPS va ishlashi\n"
    "bir-biridan farq qilgani uchun natija ham turlicha bo'ladi.\n\n"
    "⚡ Biz telefoningiz uchun imkon qadar eng kuchli va maksimal Headshot "
    "berishga yordam beradigan nastroykani tayyorlaymiz.\n"
    "🛡️ Kafolat (garantiya) berilmaydi, chunki natija telefoningizning "
    "imkoniyatlariga bog'liq.\n\n"
    "✅ Agar yuqoridagi barcha shartlarga rozi bo'lsangiz, pastdagi "
    "✅ Roziman tugmasini bosing va davom eting."
)

_KIND_LABELS = {
    "free": "🆓 Bepul nastroyka",
    "paid80": "💳 Pullik nastroyka (80% Headshot)",
    "paid97": "💳 Pullik nastroyka (97% Headshot)",
    "question": "❓ Savol",
}

_REPLY_CAPTIONS = {
    "free": "🆓 <b>Sizning bepul nastroykangiz tayyor!</b>\n\n",
    "paid80": "🎯 <b>Sizning individual nastroykangiz tayyor!</b>\n\n",
    "paid97": "🎯 <b>Sizning individual nastroykangiz tayyor!</b>\n\n",
    "question": "💬 <b>So'rovingizga javob:</b>\n\n",
}


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ==================== Kirish menyusi ====================

async def on_custom_setting_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if CUSTOM_SETTING_STICKER_ID:
        try:
            await update.message.reply_sticker(CUSTOM_SETTING_STICKER_ID)
        except TelegramError:
            pass
    await update.message.reply_text(
        ENTRY_TEXT, parse_mode="HTML", reply_markup=custom_entry_keyboard()
    )


async def on_custom_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        ENTRY_TEXT, parse_mode="HTML", reply_markup=custom_entry_keyboard()
    )


# ==================== 💳 Pullik nastroyka ====================

async def on_custom_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💳 <b>Pullik nastroyka</b>\n\nKerakli darajani tanlang 👇",
        parse_mode="HTML",
        reply_markup=custom_tiers_keyboard(),
    )


async def on_custom_tier_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tier = query.data.split(":")[-1]
    price = CUSTOM_SETTING_PRICES.get(tier, 0)
    await query.edit_message_text(
        f"🎯 <b>{tier}% Headshot Nastroyka</b>\n\n"
        f"💵 Narxi: <b>{price:,} so'm</b>".replace(",", ".") + "\n\n"
        "Xarid qilish uchun pastdagi tugmani bosing 👇",
        parse_mode="HTML",
        reply_markup=custom_tier_detail_keyboard(tier),
    )


async def on_custom_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tier = query.data.split(":")[-1]
    await query.edit_message_text(
        DISCLAIMER_TEXT,
        reply_markup=custom_agree_keyboard(tier),
    )


async def on_custom_agree(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    tier = query.data.split(":")[-1]
    price = CUSTOM_SETTING_PRICES.get(tier, 0)
    user_id = query.from_user.id

    if not db.deduct_balance(user_id, price):
        await query.answer()
        await query.edit_message_text(
            "❌ <b>Hisobingizda mablag' yetarli emas.</b>\n\n"
            "Iltimos, 💰 <b>Mening hisobim</b> bo'limidan hisobingizni to'ldiring, "
            "so'ngra qaytadan urinib ko'ring.",
            parse_mode="HTML",
            reply_markup=insufficient_balance_keyboard(),
        )
        return ConversationHandler.END

    await query.answer("✅ To'lov hisobingizdan yechildi!", show_alert=True)
    context.user_data["paid_tier"] = tier
    await query.edit_message_text(
        "✅ To'lov muvaffaqiyatli hisobingizdan yechildi!\n\n"
        "📱 Endi telefon modelingizni yozib yuboring:"
    )
    return WAITING_PAID_MODEL


async def receive_paid_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tier = context.user_data.pop("paid_tier", None)
    is_admin = _is_admin(update.effective_user.id)
    model_text = (update.message.text or "").strip()

    if not tier:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(is_admin),
        )
        return ConversationHandler.END

    if not model_text:
        context.user_data["paid_tier"] = tier
        await update.message.reply_text("⚠️ Iltimos, telefon modelingizni matn ko'rinishida yuboring.")
        return WAITING_PAID_MODEL

    kind = f"paid{tier}"
    price = CUSTOM_SETTING_PRICES.get(tier, 0)
    await update.message.reply_text(
        "✅ So'rovingiz qabul qilindi!\n\n"
        "Admin tez orada telefoningiz uchun individual nastroykani tayyorlab, "
        "shu yerga yuboradi. Iltimos, kuting.",
        reply_markup=main_menu_keyboard(is_admin),
    )
    await _notify_admin(context, update.effective_user, kind, model_text, extra=f"💵 To'langan narx: {price:,} so'm".replace(",", "."))
    return ConversationHandler.END


# ==================== 🆓 Bepul nastroyka ====================

async def on_custom_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📱 Telefon modelingizni yozib yuboring:")
    return WAITING_FREE_MODEL


async def receive_free_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    model_text = (update.message.text or "").strip()
    if not model_text:
        await update.message.reply_text("⚠️ Iltimos, telefon modelingizni matn ko'rinishida yuboring.")
        return WAITING_FREE_MODEL

    await update.message.reply_text(
        "✅ So'rovingiz qabul qilindi!\n\n"
        "Admin tez orada telefoningiz uchun bepul nastroykani tayyorlab, shu "
        "yerga yuboradi. Iltimos, kuting.",
        reply_markup=main_menu_keyboard(is_admin),
    )
    await _notify_admin(context, update.effective_user, "free", model_text)
    return ConversationHandler.END


# ==================== ❓ Savollar ====================

async def on_custom_savollar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✍️ Murojaatingizni yozib qoldiring, tezroq javob berishga harakat qilamiz."
    )
    return WAITING_CUSTOM_QUESTION


async def receive_custom_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("⚠️ Iltimos, murojaatingizni matn ko'rinishida yuboring.")
        return WAITING_CUSTOM_QUESTION

    await update.message.reply_text(
        "✅ Murojaatingiz qabul qilindi! Tez orada javob beramiz.",
        reply_markup=main_menu_keyboard(is_admin),
    )
    await _notify_admin(context, update.effective_user, "question", text)
    return ConversationHandler.END


# ==================== Umumiy: admin bildirishnomasi ====================

async def _notify_admin(context, user, kind: str, body_text: str, extra: str = ""):
    label = _KIND_LABELS.get(kind, kind)
    admin_text = (
        f"📲 <b>Yangi murojaat: {label}</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"📝 Matn:\n{body_text}\n"
        + (f"\n{extra}\n" if extra else "")
        + "\nJavob yuborish uchun pastdagi tugmani bosing 👇"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=custom_admin_reply_keyboard(kind, user.id),
        )
    except TelegramError:
        pass


async def cancel_custom_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id == ADMIN_ID
    context.user_data.pop("paid_tier", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin)
    )
    return ConversationHandler.END


# ---------- Admin javobi (matn, rasm yoki video bo'lishi mumkin) ----------

async def start_custom_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    _, kind, target_user_id = query.data.split(":", 2)
    context.user_data["custom_target_uid"] = int(target_user_id)
    context.user_data["custom_target_kind"] = kind

    await query.message.reply_text(
        "✍️ Ushbu foydalanuvchi uchun javobni yuboring "
        "(matn, rasm yoki video bo'lishi mumkin).\n\nBekor qilish uchun /bekor."
    )
    return WAITING_CUSTOM_ADMIN_REPLY


async def cancel_custom_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("custom_target_uid", None)
    context.user_data.pop("custom_target_kind", None)
    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True)
    )
    return ConversationHandler.END


async def receive_custom_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user_id = context.user_data.get("custom_target_uid")
    kind = context.user_data.get("custom_target_kind", "question")
    if not target_user_id:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.",
            reply_markup=main_menu_keyboard(True),
        )
        return ConversationHandler.END

    msg = update.message
    caption_prefix = _REPLY_CAPTIONS.get(kind, "💬 <b>Javob:</b>\n\n")

    try:
        if msg.photo:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_photo(
                chat_id=target_user_id, photo=msg.photo[-1].file_id,
                caption=caption, parse_mode="HTML",
            )
        elif msg.video:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_video(
                chat_id=target_user_id, video=msg.video.file_id,
                caption=caption, parse_mode="HTML",
            )
        elif msg.document:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_document(
                chat_id=target_user_id, document=msg.document.file_id,
                caption=caption, parse_mode="HTML",
            )
        else:
            text = caption_prefix + (msg.text_html or msg.text or "")
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

    context.user_data.pop("custom_target_uid", None)
    context.user_data.pop("custom_target_kind", None)
    return ConversationHandler.END
