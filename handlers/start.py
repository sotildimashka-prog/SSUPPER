# -*- coding: utf-8 -*-
"""/start buyrug'i, majburiy obuna tekshiruvi va pro/bot o'yinchi savoli."""

from datetime import datetime
from types import SimpleNamespace

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
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
    all_services_inline_keyboard,
    NEWS_CHANNEL_USERNAME,
    START_SERVICES_CB,
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


# ---------- 🔙 /start xabariga qaytish ----------
START_BACK_CB = "start:back"


async def _edit_in_place(query, text: str, reply_markup) -> None:
    """Callback tugma bosilganda YANGI xabar yubormasdan, ASL xabarni
    (rasm bo'lsa - caption'ini, bo'lmasa - matnini) TAHRIRLAB qo'yadi.
    Shu bilan foydalanuvchining ekrani pastga qarab surilib ketmaydi -
    hammasi bitta "forma" (xabar) ichida o'zgarib turadi."""
    msg = query.message
    try:
        if msg is not None and msg.photo:
            await query.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=reply_markup)
    except TelegramError:
        # Xabarni tahrirlab bo'lmasa (masalan, u juda eski yoki allaqachon
        # o'chirilgan) - bot to'xtab qolmasligi uchun yangi xabar yuboramiz.
        await query.get_bot().send_message(
            chat_id=query.from_user.id, text=text, parse_mode="HTML", reply_markup=reply_markup
        )


def _with_back_to_start_row(keyboard: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    """Mavjud inline klaviaturaning tagiga "⬅️ Bosh menyu" (start xabariga
    qaytish) qatorini qo'shadi - umumiy keyboards.py funksiyalariga
    tegilmaydi, faqat shu yerda (start oqimida) foydalaniladi."""
    rows = list(keyboard.inline_keyboard) + [
        [InlineKeyboardButton("⬅️ Bosh menyu", callback_data=START_BACK_CB)]
    ]
    return InlineKeyboardMarkup(rows)


async def on_start_account_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start rasmi ostidagi "👛 Hisobim" inline tugmasi - eski pastki
    tugmadagi (👛 Hisobim) xuddi shu funksiyani inline ko'rinishda beradi.
    Yangi xabar yuborish o'rniga ASL /start xabari TAHRIRLANADI - shunda
    ekran pastga qarab surilib ketmaydi."""
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
    await _edit_in_place(query, text, _with_back_to_start_row(my_account_keyboard()))


async def on_start_services_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start rasmi ostidagi "🛠️ Barcha xizmatlar" inline tugmasi -
    avval yashirilgan BARCHA bo'limlarni TO'LIQ INLINE ro'yxat qilib
    ko'rsatadi (birorta ham pastki/reply tugma chiqmaydi). Yangi xabar
    yuborish o'rniga ASL /start xabari TAHRIRLANADI."""
    query = update.callback_query
    user = query.from_user
    await query.answer()

    text = (
        "🛠️ <b>Barcha xizmatlar</b>\n\n"
        "Quyidagi tugmalar orqali botning barcha imkoniyatlaridan "
        "foydalanishingiz mumkin 👇"
    )
    await _edit_in_place(query, text, _with_back_to_start_row(all_services_inline_keyboard()))


async def on_start_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"⬅️ Bosh menyu" - foydalanuvchini ASL /start xabariga (rasm + 3 ta
    tugma) qaytaradi, yangi xabar yubormasdan, xuddi shu xabarni tahrirlab."""
    query = update.callback_query
    await query.answer()
    await _edit_in_place(query, START_CAPTION_TEXT, start_inline_keyboard())


# ---------- 🆕 "Barcha xizmatlar" ro'yxatidagi har bir band ----------
# MUHIM: Quyidagi handlerlar eski (pastki/reply tugma bilan ishlaydigan)
# funksiyalarni HECH QANDAY o'zgartirmasdan, faqat "soxta" (shim) Update
# obyekti orqali chaqiradi. Shu sababli har bir bo'limning ichki mantig'i
# (balans tekshiruvi, obuna tekshiruvi va h.k.) 100% avvalgidek ishlayveradi -
# faqat natija endi pastki tugma o'rniga inline xabar ko'rinishida yuboriladi.

def _append_back_to_services_row(reply_markup):
    """"Barcha xizmatlar" ro'yxatidan ochilgan har bir bo'lim tagiga
    "⬅️ Orqaga" (Barcha xizmatlar ro'yxatiga qaytish) tugmasini qo'shadi.
    Faqat InlineKeyboardMarkup uchun ishlaydi (ReplyKeyboard va boshqalarga
    tegilmaydi)."""
    back_row = [InlineKeyboardButton("⬅️ Orqaga", callback_data=START_SERVICES_CB)]
    if reply_markup is None:
        return InlineKeyboardMarkup([back_row])
    if not isinstance(reply_markup, InlineKeyboardMarkup):
        return reply_markup
    rows = list(reply_markup.inline_keyboard) + [back_row]
    return InlineKeyboardMarkup(rows)


class _EditingMessageProxy:
    """"Barcha xizmatlar" ro'yxatidagi bandlar eski (reply tugmali)
    handlerlarni chaqirganda, ular odatda update.message.reply_text()/
    .reply_photo() orqali YANGI xabar yuboradi - bu esa ekranni pastga
    qarab surib yuboradi. Shu proxy .reply_text()/.reply_photo() chaqiruvini
    ASL "Barcha xizmatlar" xabarini TAHRIRLASHGA (edit) almashtiradi, shunda
    hammasi bitta forma ichida o'zgaradi. Agar tahrirlash imkonsiz bo'lsa
    (masalan, matnli xabarni rasmga aylantirish kerak bo'lsa), botning
    ishlashdan to'xtab qolmasligi uchun eski xabar o'chirilib, o'rniga
    yangisi yuboriladi. Har ikkala holatda ham natijaviy klaviatura tagiga
    "⬅️ Orqaga" (Barcha xizmatlar ro'yxatiga qaytish) tugmasi qo'shiladi."""

    def __init__(self, query):
        self._query = query
        self._message = query.message

    def __getattr__(self, name):
        return getattr(self._message, name)

    async def reply_text(self, text, **kwargs):
        reply_markup = _append_back_to_services_row(kwargs.get("reply_markup"))
        parse_mode = kwargs.get("parse_mode")
        try:
            if self._message is not None and self._message.photo:
                return await self._query.edit_message_caption(
                    caption=text, parse_mode=parse_mode, reply_markup=reply_markup
                )
            return await self._query.edit_message_text(
                text=text, parse_mode=parse_mode, reply_markup=reply_markup
            )
        except TelegramError:
            try:
                await self._message.delete()
            except TelegramError:
                pass
            kwargs["reply_markup"] = reply_markup
            return await self._message.chat.send_message(text, **kwargs)

    async def reply_photo(self, photo, caption=None, **kwargs):
        reply_markup = _append_back_to_services_row(kwargs.get("reply_markup"))
        parse_mode = kwargs.get("parse_mode")
        try:
            if self._message is None or not self._message.photo:
                raise TelegramError("matnli xabarni rasmga edit qilib bo'lmaydi")
            media = InputMediaPhoto(media=photo, caption=caption, parse_mode=parse_mode)
            return await self._query.edit_message_media(media=media, reply_markup=reply_markup)
        except TelegramError:
            try:
                await self._message.delete()
            except TelegramError:
                pass
            kwargs["reply_markup"] = reply_markup
            return await self._message.chat.send_photo(photo, caption=caption, **kwargs)


def _shim_update_from_callback(query):
    """ConversationHandler holatini talab qilmaydigan oddiy "reply tugma"
    handlerlarini xavfsiz chaqirish uchun yengil "soxta" Update.
    .message => _EditingMessageProxy (haqiqiy Message kabi ishlaydi, lekin
    .reply_text()/.reply_photo() chaqirilganda YANGI xabar o'rniga ASL
    xabarni tahrirlaydi - forma pastga surilib ketmasligi uchun),
    .effective_user => tugmani haqiqatda bosgan foydalanuvchi (bot emas)."""
    proxy = _EditingMessageProxy(query)
    return SimpleNamespace(
        message=proxy,
        effective_user=query.from_user,
        effective_chat=query.message.chat if query.message else None,
        effective_message=proxy,
        callback_query=None,
    )


async def _dispatch_via_shim(handler_fn, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback orqali kelsa - shim yasab, funksiyani chaqiradi va uning
    natijasini (masalan ConversationHandler holati) qaytaradi."""
    query = update.callback_query
    if query is not None:
        fake_update = _shim_update_from_callback(query)
        return await handler_fn(fake_update, context)
    return await handler_fn(update, context)


_ALL_SERVICES_HANDLERS = None


def _load_all_services_handlers():
    """Doiraviy import (circular import)ning oldini olish uchun barcha
    handlerlar FAQAT birinchi chaqiruvda, funksiya ichida import qilinadi."""
    global _ALL_SERVICES_HANDLERS
    if _ALL_SERVICES_HANDLERS is not None:
        return _ALL_SERVICES_HANDLERS

    from handlers.newflow import (
        on_m2_services_button,
        on_m2_settings_button,
        on_m2_nicks_button,
        on_m2_payments_button,
        on_m2_diamonds_button,
    )
    from handlers.image_gen import on_rasm_button
    from handlers.music_gen import on_music_create_button
    from handlers.store import on_store_button
    from handlers.games import on_games_button
    from handlers.gifts import on_gifts_button
    from handlers.pro_sub import on_pro_sub_button
    from handlers.withdraw_win import on_withdraw_win_button
    from handlers.gift_order import on_gift_order_button
    from handlers.withdraw import on_withdraw_button
    from bot import on_orders_channel_button

    _ALL_SERVICES_HANDLERS = {
        "services": on_m2_services_button,
        "settings": on_m2_settings_button,
        "nicks": on_m2_nicks_button,
        "rasm": on_rasm_button,
        # "video" bu yerda YO'Q - u alohida (ConversationHandler holatini
        # to'g'ri saqlash uchun) on_video_button_from_services orqali
        # ishlaydi, pastga qarang.
        "music": on_music_create_button,
        "store": on_store_button,
        "payments": on_m2_payments_button,
        "games": on_games_button,
        "gifts": on_gifts_button,
        "prosub": on_pro_sub_button,
        "withdrawwin": on_withdraw_win_button,
        "orders": on_orders_channel_button,
        "giftorder": on_gift_order_button,
        "diamonds": on_m2_diamonds_button,
        "withdraw": on_withdraw_button,
    }
    return _ALL_SERVICES_HANDLERS


async def on_all_services_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"🛠️ Barcha xizmatlar" ro'yxatidagi (svcall:<key>) har qanday band."""
    query = update.callback_query
    await query.answer()

    key = query.data.split(":", 1)[1] if query.data and ":" in query.data else ""
    handler_fn = _load_all_services_handlers().get(key)
    if handler_fn is None:
        return

    await _dispatch_via_shim(handler_fn, update, context)


async def on_video_button_from_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"🎬 Video Yasash" - "Barcha xizmatlar" ro'yxatidan bosilganda.
    video_conv ConversationHandler'ga ALOHIDA entry_point sifatida
    qo'shiladi (bot.py), shunda PTB navbatdagi holatni (WAITING_VIDEO_PROMPT)
    to'g'ri saqlaydi va foydalanuvchi keyingi xabarini kutish ishlayveradi."""
    from handlers.video_gen import on_video_button

    query = update.callback_query
    if query is not None:
        await query.answer()
    return await _dispatch_via_shim(on_video_button, update, context)


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
