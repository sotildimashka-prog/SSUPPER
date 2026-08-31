# -*- coding: utf-8 -*-
"""/start buyrug'i, majburiy obuna tekshiruvi va pro/bot o'yinchi savoli."""

from datetime import datetime

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID, BOT_NAME
from keyboards import (
    subscription_keyboard,
    main_menu_keyboard,
    full_menu_keyboard,
    my_account_keyboard,
    player_type_keyboard,
    add_to_group_keyboard,
    language_keyboard,
    portal_button_row,
    start_inline_keyboard,
    NEWS_CHANNEL_USERNAME,
)
from handlers.subscription import get_unsubscribed_channels

PROMO_USER_IDS = {
    812987290,
    7961289069,
    8320859741,
    8410029692,
    7616169959,
    5941100214,
    6520050836,
    1130408540,
    6388678313,
}
PROMO_DIAMOND_AMOUNT = 7

# ---------- 🌐 Til tanlash ----------

LANGUAGE_PROMPT_TEXT = (
    "🌐 <b>Tilni tanlang / Выберите язык</b>\n\n"
    "Iltimos, quyidagi tugmalardan birini bosing 👇\n"
    "Пожалуйста, нажмите одну из кнопок ниже 👇"
)


def first_greeting_text(first_name: str, lang: str = "uz") -> str:
    name = first_name or ("do'stim" if lang == "uz" else "друг")
    if lang == "ru":
        return (
            f"Здравствуйте, {name} 👋\n\n"
            "📋 Вы можете открыть меню, нажав нужную кнопку.\n"
            "🤖 Я бот, который оказывает лучший сервис для игры Free Fire.\n\n"
            "❓ Есть вопросы? Не проблема! Нажмите кнопку \"📬 Вопросы (FAQ)\", "
            "и мы постараемся ответить как можно быстрее."
        )
    return (
        f"Assalomu aleykum, {name} 👋\n\n"
        "📋 O'zingizga kerakli tugmani bosish orqali menyuni chiqarishingiz mumkin.\n"
        "🤖 Men Free Fire o'yini uchun mukammal xizmat ko'rsatadigan botman.\n\n"
        "❓ Savollaringiz bormi? Hammasi joyida! \"📬 Savollar (FAQ)\" tugmasini "
        "bosing va biz imkon qadar tezroq javob berishga harakat qilamiz."
    )


def subscribe_text(lang: str = "uz") -> str:
    if lang == "ru":
        return (
            "📢 <b>Чтобы пользоваться ботом, сначала подпишитесь на каналы ниже!</b>\n\n"
            "Если вы не подписаны, бот пока не будет работать ⛔️\n"
            "После подписки на все каналы нажмите кнопку "
            "<b>✅ Я подписался</b> внизу 👇"
        )
    return (
        "📢 <b>Botdan foydalanish uchun avval quyidagi kanallarga obuna bo'ling!</b>\n\n"
        "Obuna bo'lmasangiz, bot hali ishlamaydi ⛔️\n"
        "Barcha kanallarga obuna bo'lgach, pastdagi <b>✅ Obuna bo'ldim</b> "
        "tugmasini bosing 👇"
    )


def player_type_question(lang: str = "uz") -> str:
    if lang == "ru":
        return "🎮 <b>Вы PRO игрок или BOT игрок?</b> 👇"
    return "🎮 <b>Siz PRO o'yinchimisiz yoki BOT o'yinchimisiz?</b> 👇"


def add_to_group_text(lang: str = "uz") -> str:
    if lang == "ru":
        return (
            "➕ <b>Добавьте бота в свою группу!</b>\n\n"
            "Наслаждайтесь настройками и новостями Free Fire вместе с друзьями. "
            "Нажмите кнопку ниже 👇"
        )
    return (
        "➕ <b>Botni guruhingizga qo'shing!</b>\n\n"
        "Do'stlaringiz bilan birga Free Fire nastroykalari va yangiliklaridan "
        "bahramand bo'ling. Pastdagi tugmani bosing 👇"
    )


def main_menu_ready_text(lang: str = "uz") -> str:
    if lang == "ru":
        return "👇 Главное меню готово:"
    return "👇 Asosiy menyu tayyor:"


def official_site_text(lang: str = "uz") -> str:
    if lang == "ru":
        return (
            "🌐 <b>Наш официальный сайт</b>\n\n"
            "Перейдите на Free Fire Portal, нажав кнопку ниже 👇"
        )
    return (
        "🌐 <b>Bizning rasmiy sayt</b>\n\n"
        "Free Fire Portal'ga o'tish uchun pastdagi tugmani bosing 👇"
    )


# Eski nomlar (SUBSCRIBE_TEXT, PLAYER_TYPE_QUESTION, ADD_TO_GROUP_TEXT) boshqa
# modullarda ishlatilgan bo'lishi mumkin - orqaga moslik uchun (uz tilida) saqlanadi.
SUBSCRIBE_TEXT = subscribe_text("uz")
PLAYER_TYPE_QUESTION = player_type_question("uz")
ADD_TO_GROUP_TEXT = add_to_group_text("uz")


async def notify_admin_new_user(context: ContextTypes.DEFAULT_TYPE, user):
    text = (
        "🆕 <b>Yangi foydalanuvchi</b>\n\n"
        f"👤 Ism: {user.first_name or '-'}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🔗 Username: @{user.username if user.username else '—'}\n"
        f"🕒 Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="HTML")
    except TelegramError:
        pass


async def _send_player_type_question(update_or_query, context: ContextTypes.DEFAULT_TYPE, chat_id: int, lang: str = "uz"):
    await context.bot.send_message(
        chat_id=chat_id,
        text=player_type_question(lang),
        parse_mode="HTML",
        reply_markup=player_type_keyboard(),
    )


async def _send_official_site_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, lang: str = "uz"):
    await context.bot.send_message(
        chat_id=chat_id,
        text=official_site_text(lang),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([portal_button_row()]),
    )


async def _continue_after_language(update: Update, context: ContextTypes.DEFAULT_TYPE, user, lang: str):
    """Til tanlangandan (yoki avval tanlangan bo'lsa) so'ng davom etadigan qism:
    salomlashuv -> majburiy obuna -> pro/bot savoli -> asosiy menyu."""

    # 1) Birinchi salomlashuv
    await context.bot.send_message(
        chat_id=user.id,
        text=first_greeting_text(user.first_name, lang),
        parse_mode="HTML",
    )

    # 2) Majburiy obuna tekshiruvi
    unsubscribed = await get_unsubscribed_channels(user.id, context)
    if unsubscribed:
        await context.bot.send_message(
            chat_id=user.id,
            text=subscribe_text(lang),
            parse_mode="HTML",
            reply_markup=subscription_keyboard(),
        )
        return

    # Agar allaqachon obuna bo'lgan bo'lsa - to'g'ridan-to'g'ri asosiy menyuga
    is_admin = user.id == ADMIN_ID
    await context.bot.send_message(
        chat_id=user.id,
        text=main_menu_ready_text(lang),
        reply_markup=main_menu_keyboard(is_admin),
    )
    await _send_official_site_message(context, user.id, lang)


# ---------- 🆕 /start uchun rasm + 3 ta inline tugma ----------
# MUHIM: Foydalanuvchi so'rovi bo'yicha /start bosilganda chiqadigan barcha
# eski xabarlar (til tanlash, salomlashuv, majburiy obuna taklifi, pro/bot
# savoli, guruhga qo'shish taklifi, rasmiy sayt xabari) OLIB TASHLANDI.
# Ular hali ham shu faylda funksiya sifatida saqlanmoqda (hech narsa
# o'chirilmagan) - faqat start_command ichidan chaqirilmayapti.
#
# Rasm manzili: assets/start_banner.jpg. Botni ishga tushirishdan oldin
# shu nomdagi rasmni "assets" papkasiga qo'ying (yoki quyidagi
# START_PHOTO_PATH ni o'zgartiring). Agar rasm topilmasa, bot xatoga
# tushmaydi - shunchaki oddiy matnli xabar + tugmalar yuboriladi.
START_PHOTO_PATH = "assets/start_banner.jpg"

START_CAPTION_TEXT = (
    "👋 <b>Xush kelibsiz!</b>\n\n"
    "🤖 Men Free Fire o'yini uchun mukammal xizmat ko'rsatadigan botman.\n\n"
    "👇 Kerakli bo'limni tanlang:"
)


async def _send_start_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    try:
        with open(START_PHOTO_PATH, "rb") as photo_file:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo_file,
                caption=START_CAPTION_TEXT,
                parse_mode="HTML",
                reply_markup=start_inline_keyboard(),
            )
    except (FileNotFoundError, OSError, TelegramError):
        # Rasm topilmasa yoki yuborib bo'lmasa - hech bo'lmasa tugmalar
        # bilan matnli xabar chiqadi (bot to'xtab qolmasligi uchun).
        await context.bot.send_message(
            chat_id=chat_id,
            text=START_CAPTION_TEXT,
            parse_mode="HTML",
            reply_markup=start_inline_keyboard(),
        )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = db.add_user_if_new(user.id, user.first_name or "", user.username or "")

    if is_new:
        await notify_admin_new_user(context, user)

    if user.id in PROMO_USER_IDS and not db.has_promo_credit(user.id):
        db.add_quiz_diamonds(user.id, PROMO_DIAMOND_AMOUNT)
        db.mark_promo_credited(user.id)
        try:
            await update.message.reply_text(
                f"🎁 Sizga sovg'a sifatida {PROMO_DIAMOND_AMOUNT} dona almaz taqdim etildi!"
            )
        except TelegramError:
            pass

    await _send_start_message(context, user.id)


async def on_start_account_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start rasmi ostidagi "👛 Hisobim" inline tugmasi - eski pastki
    tugmadagi (👛 Hisobim) xuddi shu funksiyani inline ko'rinishda beradi."""
    query = update.callback_query
    user = query.from_user
    await query.answer()

    diamonds = db.get_quiz_diamonds(user.id)
    money = db.get_balance(user.id)
    text = (
        "👛 <b>Hisobim</b>\n\n"
        f"💎 Almaz: <b>{diamonds}</b>\n"
        f"💵 Pul: <b>{money:,} so'm</b>\n\n".replace(",", ".")
        + "Barcha to'lov usullari haqida ma'lumot olish uchun pastdagi tugmani bosing 👇"
    )
    await context.bot.send_message(
        chat_id=user.id,
        text=text,
        parse_mode="HTML",
        reply_markup=my_account_keyboard(),
    )


async def on_start_services_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start rasmi ostidagi "🛠️ Barcha xizmatlar" inline tugmasi -
    avval yashirilgan BARCHA pastki (reply) tugmalarni qaytadan chiqaradi."""
    query = update.callback_query
    user = query.from_user
    await query.answer()

    is_admin = user.id == ADMIN_ID
    await context.bot.send_message(
        chat_id=user.id,
        text=(
            "🛠️ <b>Barcha xizmatlar</b>\n\n"
            "Quyidagi tugmalar orqali botning barcha imkoniyatlaridan "
            "foydalanishingiz mumkin 👇"
        ),
        parse_mode="HTML",
        reply_markup=full_menu_keyboard(is_admin),
    )


async def on_language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🇺🇿 / 🇷🇺 tugmasi bosilganda tilni saqlaydi va qolgan /start oqimini davom ettiradi."""
    query = update.callback_query
    user = query.from_user
    await query.answer()

    lang = query.data.split(":", 1)[1] if ":" in query.data else "uz"
    if lang not in ("uz", "ru"):
        lang = "uz"
    db.set_user_language(user.id, lang)

    try:
        await query.message.delete()
    except TelegramError:
        pass

    await _continue_after_language(update, context, user, lang)


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    lang = db.get_user_language(user.id) or "uz"

    unsubscribed = await get_unsubscribed_channels(user.id, context)
    if unsubscribed:
        alert_text = (
            "⛔️ Бот пока не работает! Сначала подпишитесь на все каналы."
            if lang == "ru"
            else "⛔️ Bot hali ishlamaydi! Avval barcha kanallarga obuna bo'ling."
        )
        await query.answer(alert_text, show_alert=True)
        return

    is_admin = user.id == ADMIN_ID
    try:
        await query.message.delete()
    except TelegramError:
        pass

    # 3) Asosiy menyu
    await context.bot.send_message(
        chat_id=user.id,
        text=main_menu_ready_text(lang),
        reply_markup=main_menu_keyboard(is_admin),
    )
    await _send_official_site_message(context, user.id, lang)


async def on_player_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pro yoki Bot o'yinchi tanlanganda - ikkalasida ham guruhga qo'shish taklifi chiqadi."""
    query = update.callback_query
    await query.answer()
    lang = db.get_user_language(query.from_user.id) or "uz"

    me = await context.bot.get_me()
    try:
        await query.edit_message_text(
            add_to_group_text(lang),
            parse_mode="HTML",
            reply_markup=add_to_group_keyboard(me.username),
        )
    except TelegramError:
        pass
