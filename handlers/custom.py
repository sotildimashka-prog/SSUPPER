# -*- coding: utf-8 -*-
"""📲 Shaxsiy nastroyka (Pullik / Bepul).

Bepul: foydalanuvchi telefon modelini yozadi -> admin qo'lda nastroyka yuboradi.
Pullik: foydalanuvchi tarifni tanlaydi -> shartga rozilik bildiradi -> telefon
modelini yozadi -> admin bilan kelishib, nastroyka yuboriladi.
"""

from types import SimpleNamespace

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    custom_entry_keyboard,
    paid_tiers_keyboard,
    paid_tier_detail_keyboard,
    paid_disclaimer_keyboard,
    custom_admin_keyboard,
)
from handlers.orders_channel import announce_order_completed

WAITING_FREE_MODEL, WAITING_PAID_MODEL, WAITING_CUSTOM_ADMIN_REPLY = range(3)

# ⚠️ NARXLAR HOZIRCHA PLACEHOLDER - aniq summani ayting, men shu yerga qo'yib beraman.
PAID_TIERS = {
    "hs80": {"title": "🎯 80% Headshot", "price": "narxi kelishiladi"},
    "hs97": {"title": "🎯 97% Headshot", "price": "narxi kelishiladi"},
}


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ---------------------------------------------------------------------------
# Kirish nuqtasi va orqaga
# ---------------------------------------------------------------------------
async def on_custom_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📲 <b>Shaxsiy nastroyka</b>\n\nQuyidagilardan birini tanlang 👇",
        parse_mode="HTML",
        reply_markup=custom_entry_keyboard(),
    )


async def on_custom_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📲 <b>Shaxsiy nastroyka</b>\n\nQuyidagilardan birini tanlang 👇",
        parse_mode="HTML",
        reply_markup=custom_entry_keyboard(),
    )


# ---------------------------------------------------------------------------
# 🆓 Bepul nastroyka
# ---------------------------------------------------------------------------
async def on_custom_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "🆓 <b>Bepul nastroyka</b>\n\n"
        "Telefon modelingizni <b>to'liq va aniq</b> yozib yuboring "
        "(brend, model, agar bilsangiz RAM/protsessor bilan).\n\n"
        "Masalan: <i>Samsung Galaxy A54, 8GB RAM</i>\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_FREE_MODEL


async def cancel_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END


async def receive_free_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    model_text = (update.message.text or "").strip()

    if not model_text:
        await update.message.reply_text("⚠️ Iltimos, telefon modelini matn ko'rinishida yuboring.")
        return WAITING_FREE_MODEL

    is_admin = _is_admin(user.id)
    await update.message.reply_text(
        "✅ So'rovingiz qabul qilindi!\n\n"
        "Admin tez orada telefoningiz uchun individual nastroykani tayyorlab yuboradi.",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "🆓 <b>Yangi BEPUL nastroyka so'rovi</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"📱 Telefon modeli:\n{model_text}"
    )
    context.bot_data.setdefault("pending_orders", {})[user.id] = {
        "type_label": "🆓 Bepul nastroyka",
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
            reply_markup=custom_admin_keyboard(user.id, order_kind="nastroyka_free"),
        )
    except TelegramError:
        pass

    return ConversationHandler.END


# ---------------------------------------------------------------------------
# 💰 Pullik nastroyka
# ---------------------------------------------------------------------------
async def on_custom_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💰 <b>Pullik nastroyka</b>\n\nTarifni tanlang 👇",
        parse_mode="HTML",
        reply_markup=paid_tiers_keyboard(),
    )


async def on_paid_tier_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    tier = PAID_TIERS.get(key)
    if not tier:
        return

    text = f"{tier['title']}\n\n💰 Narxi: {tier['price']}\n\nXarid qilish uchun pastdagi tugmani bosing 👇"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=paid_tier_detail_keyboard(key))


async def on_paid_buy_clicked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    tier = PAID_TIERS.get(key, {})

    text = (
        "⚠️ <b>Ogohlantirish</b>\n\n"
        f"Siz \"{tier.get('title', '')}\" xizmatini tanladingiz.\n"
        f"💰 Narxi: {tier.get('price', '-')}\n\n"
        "Davom etish uchun shartlarga rozilik bildiring 👇"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=paid_disclaimer_keyboard(key))


async def on_paid_agree(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    context.user_data["paid_tier_key"] = key

    await query.message.reply_text(
        "📱 Telefon modelingizni to'liq yozib yuboring (brend + model).\n\nBekor qilish uchun /bekor."
    )
    return WAITING_PAID_MODEL


async def cancel_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("paid_tier_key", None)
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END


async def receive_paid_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    model_text = (update.message.text or "").strip()

    if not model_text:
        await update.message.reply_text("⚠️ Iltimos, telefon modelini matn ko'rinishida yuboring.")
        return WAITING_PAID_MODEL

    key = context.user_data.pop("paid_tier_key", None)
    tier = PAID_TIERS.get(key, {})
    is_admin = _is_admin(user.id)

    await update.message.reply_text(
        "✅ So'rovingiz qabul qilindi! Admin siz bilan to'lov yuzasidan bog'lanadi.",
        reply_markup=main_menu_keyboard(is_admin),
    )

    admin_text = (
        "💰 <b>Yangi PULLIK nastroyka buyurtmasi!</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"🎯 Tarif: {tier.get('title', key)}\n"
        f"💰 Narxi: {tier.get('price', '-')}\n"
        f"📱 Telefon modeli:\n{model_text}"
    )
    context.bot_data.setdefault("pending_orders", {})[user.id] = {
        "type_label": "💰 Pullik nastroyka",
        "user_id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "info": f"🎯 Tarif: {tier.get('title', key)}\n📱 Telefon modeli: {model_text}",
    }
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=custom_admin_keyboard(user.id, order_kind="nastroyka_paid"),
        )
    except TelegramError:
        pass

    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Admin javobi (Bepul va Pullik ikkalasi uchun ham umumiy)
# ---------------------------------------------------------------------------
async def start_custom_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    parts = query.data.split(":", 2)
    if len(parts) == 3:
        _, order_kind, target_user_id = parts
    else:
        # Eski formatdagi callback ("customreply:{user_id}") bilan ham
        # moslashuvchan ishlashi uchun.
        order_kind, target_user_id = "nastroyka", parts[1]
    target_user_id = int(target_user_id)
    context.user_data["custom_target_uid"] = target_user_id
    context.user_data["custom_target_kind"] = order_kind

    _PROMPTS = {
        "rasm": "✍️ Ushbu foydalanuvchi uchun tayyor rasmni yuboring.\n\nBekor qilish uchun /bekor.",
        "video": "✍️ Ushbu foydalanuvchi uchun tayyor videoni yuboring.\n\nBekor qilish uchun /bekor.",
    }
    prompt_text = _PROMPTS.get(
        order_kind,
        "✍️ Ushbu foydalanuvchi uchun nastroykani yuboring "
        "(matn, rasm yoki video bo'lishi mumkin).\n\nBekor qilish uchun /bekor.",
    )

    await query.message.reply_text(prompt_text)
    return WAITING_CUSTOM_ADMIN_REPLY


async def cancel_custom_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("custom_target_uid", None)
    context.user_data.pop("custom_target_kind", None)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True))
    return ConversationHandler.END


async def receive_custom_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user_id = context.user_data.get("custom_target_uid")
    order_kind = context.user_data.get("custom_target_kind", "nastroyka")
    if not target_user_id:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.", reply_markup=main_menu_keyboard(True)
        )
        return ConversationHandler.END

    msg = update.message
    _CAPTION_PREFIXES = {
        "nastroyka_free": "🎯 <b>Sizning individual nastroykangiz tayyor!</b>\n\n",
        "nastroyka_paid": "🎯 <b>Sizning individual nastroykangiz tayyor!</b>\n\n",
        "nastroyka": "🎯 <b>Sizning individual nastroykangiz tayyor!</b>\n\n",
        "rasm": "💎 <b>Sizning maxsus rasmingiz tayyor!</b>\n\n",
        "video": "🎬 <b>Sizning videongiz tayyor!</b>\n\n",
    }
    caption_prefix = _CAPTION_PREFIXES.get(order_kind, "🎯 <b>Sizning individual nastroykangiz tayyor!</b>\n\n")

    try:
        if msg.photo:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_photo(
                chat_id=target_user_id, photo=msg.photo[-1].file_id, caption=caption, parse_mode="HTML"
            )
        elif msg.video:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_video(
                chat_id=target_user_id, video=msg.video.file_id, caption=caption, parse_mode="HTML"
            )
        elif msg.document:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_document(
                chat_id=target_user_id, document=msg.document.file_id, caption=caption, parse_mode="HTML"
            )
        else:
            text = caption_prefix + (msg.text_html or msg.text or "")
            await context.bot.send_message(chat_id=target_user_id, text=text, parse_mode="HTML")

        await update.message.reply_text(
            "✅ Foydalanuvchiga muvaffaqiyatli yuborildi!", reply_markup=main_menu_keyboard(True)
        )

        await _announce_completed(context, order_kind, target_user_id)
    except TelegramError:
        await update.message.reply_text(
            "❌ Yuborishda xatolik yuz berdi (foydalanuvchi botni bloklagan bo'lishi mumkin).",
            reply_markup=main_menu_keyboard(True),
        )

    context.user_data.pop("custom_target_uid", None)
    context.user_data.pop("custom_target_kind", None)
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# 📢 Bajarilgan buyurtmani @buyurtmalar_ff kanaliga e'lon qilish
# ---------------------------------------------------------------------------
_ORDER_KIND_LABELS = {
    "nastroyka_free": "🆓 Bepul nastroyka",
    "nastroyka_paid": "💰 Pullik nastroyka",
    "nastroyka": "📲 Shaxsiy nastroyka",
    "rasm": "💎 Maxsus rasm",
    "video": "🎬 Video yasash",
}


async def _announce_completed(context: ContextTypes.DEFAULT_TYPE, order_kind: str, target_user_id: int):
    pending = context.bot_data.get("pending_orders", {}).pop(target_user_id, None)
    label = _ORDER_KIND_LABELS.get(order_kind, "📲 Buyurtma")
    info = ""

    if pending:
        label = pending.get("type_label", label)
        info = pending.get("info", "")
        user_id = pending.get("user_id", target_user_id)
        first_name = pending.get("first_name")
        username = pending.get("username")
    else:
        user_id = target_user_id
        first_name = None
        username = None
        try:
            chat = await context.bot.get_chat(target_user_id)
            first_name = getattr(chat, "first_name", None)
            username = getattr(chat, "username", None)
        except TelegramError:
            pass

    order_user = SimpleNamespace(id=user_id, first_name=first_name, username=username)
    await announce_order_completed(context.bot, label, order_user, info)
