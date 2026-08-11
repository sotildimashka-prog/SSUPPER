# -*- coding: utf-8 -*-
"""🎵 Musiqa yaratish bo'limi.

Oqim:
1) Foydalanuvchi "🎵 Musiqa yaratish" tugmasini bosadi -> janr tanlash
   (Jazz / Bass / Sokin / Rep) inline tugmalari chiqadi (yonma-yon, 2 tadan).
2) Janr tanlangach -> "Qanday musiqa tayyorlaymiz? Batafsil yozib yuboring"
   deb so'raladi, foydalanuvchi matn yozadi.
3) Matn qabul qilingach -> til tanlash (bayroqlar bilan: 🇺🇿 🇷🇺 🇸🇦 🇬🇧).
4) Til tanlangach -> "🎧 Musiqa tayyorlash" tugmasi chiqadi.
5) Tugma bosilganda:
   - Kunlik limit tekshiriladi (oddiy foydalanuvchi: 1 marta/kun,
     Pro obuna sotib olganlar: 10 marta/kun). Limit tugagan bo'lsa,
     "Limitingiz tugadi..." xabari va Pro sotib olish tugmasi chiqadi.
   - Limit yetarli bo'lsa, ekranda son tinmay aylanib turadigan
     progress-animatsiya boshlanadi (1->100->1->100 ...) va bu holat
     ADMIN tayyor musiqani yuborguncha davom etadi.
6) Admin (@auwsn) so'rovni to'liq holda oladi va "🎵 Musiqani yuborish"
   tugmasini bosib, tayyor faylni (audio/ovozli xabar/hujjat) yuboradi.
   Fayl yuborilgan zahoti foydalanuvchidagi animatsiya to'xtaydi va
   musiqa unga yetkaziladi.
"""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

import database as db
from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    music_genre_keyboard,
    music_language_keyboard,
    music_prepare_keyboard,
    music_admin_send_keyboard,
    music_limit_reached_keyboard,
    MUSIC_GENRES,
    MUSIC_LANGS,
)
from handlers.subscription import require_subscription

WAITING_MUSIC_PROMPT, WAITING_MUSIC_ADMIN_REPLY = range(2)

# Oddiy foydalanuvchi va Pro obunachilar uchun kunlik musiqa yaratish limiti.
FREE_DAILY_LIMIT = 1
PRO_DAILY_LIMIT = 10

# "Kutib turing" matnini jonli qilish uchun almashinadigan nuqtalar.
_WAIT_DOTS = [".", "..", "...", "...."]

# user_id -> {"task": asyncio.Task, "chat_id": int, "message_id": int}
# Musiqa tayyor bo'lguncha aylanayotgan animatsiyalarni saqlab turadi, shu
# orqali admin faylni yuborganda tegishli animatsiyani to'xtatamiz.
_ANIMATIONS: dict[int, dict] = {}


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ---------------------------------------------------------------------------
# 1) Kirish nuqtasi: "🎵 Musiqa yaratish" tugmasi
# ---------------------------------------------------------------------------
async def on_music_create_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_subscription(update, context):
        return
    await update.message.reply_text(
        "🎵 <b>Musiqa yaratish</b>\n\n"
        "Avval qaysi <b>janrda</b> musiqa yaratishni tanlang 👇",
        parse_mode="HTML",
        reply_markup=music_genre_keyboard(),
    )


async def on_music_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    is_admin = _is_admin(query.from_user.id)
    try:
        await query.message.delete()
    except TelegramError:
        pass
    await query.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))


# ---------------------------------------------------------------------------
# 2) Janr tanlandi -> batafsil yozish so'raladi (ConversationHandler kirish nuqtasi)
# ---------------------------------------------------------------------------
async def on_music_genre_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    genre = query.data.split(":", 2)[2]
    if genre not in MUSIC_GENRES:
        return ConversationHandler.END

    context.user_data["music_genre"] = genre
    genre_label = MUSIC_GENRES[genre][0]

    await query.edit_message_text(
        f"✅ Janr: <b>{genre_label}</b>\n\n"
        "✍️ Qanday musiqa tayyorlaymiz? <b>Batafsil</b> yozib yuboring "
        "(mavzu, kayfiyat, kim haqida va h.k.)\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_MUSIC_PROMPT


async def cancel_music_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("music_genre", None)
    context.user_data.pop("music_prompt", None)
    is_admin = _is_admin(update.effective_user.id)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(is_admin))
    return ConversationHandler.END


async def receive_music_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt_text = (update.message.text or "").strip()
    if not prompt_text:
        await update.message.reply_text("⚠️ Iltimos, matn ko'rinishida batafsil yozing.")
        return WAITING_MUSIC_PROMPT

    genre = context.user_data.get("music_genre")
    if not genre or genre not in MUSIC_GENRES:
        is_admin = _is_admin(update.effective_user.id)
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.", reply_markup=main_menu_keyboard(is_admin)
        )
        return ConversationHandler.END

    context.user_data["music_prompt"] = prompt_text

    await update.message.reply_text(
        "✅ Qabul qilindi!\n\n"
        "Endi musiqa qaysi <b>tilda</b> bo'lishini tanlang 👇",
        parse_mode="HTML",
        reply_markup=music_language_keyboard(genre),
    )
    return ConversationHandler.END


async def on_music_back_to_genre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎵 <b>Musiqa yaratish</b>\n\n"
        "Avval qaysi <b>janrda</b> musiqa yaratishni tanlang 👇",
        parse_mode="HTML",
        reply_markup=music_genre_keyboard(),
    )


# ---------------------------------------------------------------------------
# 3) Til tanlandi -> "Musiqa tayyorlash" tugmasi
# ---------------------------------------------------------------------------
async def on_music_lang_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, _, genre, lang = query.data.split(":", 3)
    if genre not in MUSIC_GENRES or lang not in MUSIC_LANGS:
        return

    genre_label = MUSIC_GENRES[genre][0]
    lang_label = MUSIC_LANGS[lang][0]
    prompt = context.user_data.get("music_prompt", "-")

    await query.edit_message_text(
        f"✅ Janr: <b>{genre_label}</b>\n"
        f"✅ Til: <b>{lang_label}</b>\n"
        f"📝 Tavsif: <i>{prompt}</i>\n\n"
        "Tayyor bo'lsangiz, pastdagi tugmani bosing 👇",
        parse_mode="HTML",
        reply_markup=music_prepare_keyboard(genre, lang),
    )


async def on_music_back_to_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    genre = query.data.split(":", 2)[2]
    if genre not in MUSIC_GENRES:
        return
    genre_label = MUSIC_GENRES[genre][0]
    await query.edit_message_text(
        f"✅ Janr: <b>{genre_label}</b>\n\n"
        "Endi musiqa qaysi <b>tilda</b> bo'lishini tanlang 👇",
        parse_mode="HTML",
        reply_markup=music_language_keyboard(genre),
    )


# ---------------------------------------------------------------------------
# 4) "Musiqa tayyorlash" bosildi -> limit tekshiruvi + aylanuvchi animatsiya
# ---------------------------------------------------------------------------
def _progress_frame(i: int, genre_short: str, lang_short: str, prompt: str) -> str:
    percent = (i % 100) + 1
    dots = _WAIT_DOTS[i % len(_WAIT_DOTS)]
    bar_filled = round(percent / 10)
    bar = "▓" * bar_filled + "░" * (10 - bar_filled)
    return (
        f"🎶 <b>Musiqa yaratilmoqda, kutib turing{dots}</b>\n\n"
        f"{bar}  <b>{percent}%</b>\n\n"
        f"🎧 Janr: {genre_short}\n"
        f"🌐 Til: {lang_short}\n"
        f"📝 Tavsif: <i>{prompt}</i>"
    )


async def _run_loading_animation(bot, chat_id: int, message_id: int, genre_short: str, lang_short: str, prompt: str):
    """Admin tayyor musiqani yuborguncha son tinmay aylanib turadi."""
    i = 0
    try:
        while True:
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=_progress_frame(i, genre_short, lang_short, prompt),
                    parse_mode="HTML",
                )
            except TelegramError:
                pass
            i += 1
            await asyncio.sleep(1.2)
    except asyncio.CancelledError:
        pass


async def _stop_animation(user_id: int, bot, final_text: str | None = None):
    entry = _ANIMATIONS.pop(user_id, None)
    if not entry:
        return
    task = entry.get("task")
    if task and not task.done():
        task.cancel()
        try:
            await task
        except Exception:
            pass
    if final_text:
        try:
            await bot.edit_message_text(
                chat_id=entry["chat_id"], message_id=entry["message_id"], text=final_text, parse_mode="HTML"
            )
        except TelegramError:
            pass


async def on_music_prepare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, _, genre, lang = query.data.split(":", 3)
    if genre not in MUSIC_GENRES or lang not in MUSIC_LANGS:
        return

    user = query.from_user
    genre_label, genre_short = MUSIC_GENRES[genre]
    lang_label, lang_short = MUSIC_LANGS[lang]
    prompt = context.user_data.get("music_prompt", "-")

    # --- Kunlik limitni tekshirish ---
    is_pro = db.is_pro_user(user.id)
    limit = PRO_DAILY_LIMIT if is_pro else FREE_DAILY_LIMIT
    used_today = db.get_music_generated_today(user.id)

    if used_today >= limit:
        if is_pro:
            text = (
                "⛔️ <b>Limitingiz tugadi!</b>\n\n"
                f"👑 Pro obuna doirasida kuniga <b>{PRO_DAILY_LIMIT} tagacha</b> musiqa yaratishingiz mumkin.\n"
                "Ertaga qaytadan urinib ko'ring 🙏"
            )
            await query.edit_message_text(text, parse_mode="HTML")
        else:
            text = (
                "⛔️ <b>Limitingiz tugadi!</b>\n\n"
                "Oddiy foydalanuvchilar kuniga <b>1 marta</b> musiqa yaratishlari mumkin.\n"
                "🔁 Ertaga qaytadan urinib ko'ring yoki\n"
                f"👑 Pro obuna sotib oling — kuniga <b>{PRO_DAILY_LIMIT} tagacha</b> musiqa yaratasiz!"
            )
            await query.edit_message_text(
                text, parse_mode="HTML", reply_markup=music_limit_reached_keyboard()
            )
        return

    db.increment_music_generated(user.id)

    # --- Animatsiyani boshlash: admin musiqani yuborguncha davom etadi ---
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    # Agar shu foydalanuvchi uchun eski animatsiya bo'lsa (masalan qayta
    # bosilgan bo'lsa), avval uni to'xtatamiz.
    await _stop_animation(user.id, context.bot)

    task = asyncio.create_task(
        _run_loading_animation(context.bot, chat_id, message_id, genre_short, lang_short, prompt)
    )
    _ANIMATIONS[user.id] = {"task": task, "chat_id": chat_id, "message_id": message_id}

    admin_text = (
        "🎵 <b>Yangi MUSIQA YARATISH so'rovi!</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"🎧 Janr: {genre_label}\n"
        f"🌐 Til: {lang_label}\n"
        f"📝 Tavsif:\n{prompt}"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=music_admin_send_keyboard(user.id, genre, lang),
        )
    except TelegramError:
        pass


# ---------------------------------------------------------------------------
# 5) Admin javobi: tayyor musiqani foydalanuvchiga yuborish
# ---------------------------------------------------------------------------
async def start_music_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu funksiya faqat admin uchun.", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    _, target_user_id, genre, lang = query.data.split(":", 3)
    context.user_data["music_target_uid"] = int(target_user_id)
    context.user_data["music_target_genre"] = genre
    context.user_data["music_target_lang"] = lang

    genre_label = MUSIC_GENRES.get(genre, (genre, genre))[0]
    lang_label = MUSIC_LANGS.get(lang, (lang, lang))[0]

    await query.message.reply_text(
        f"🎵 <b>{genre_label} / {lang_label}</b>\n\n"
        "Ushbu foydalanuvchi uchun tayyor musiqa faylini yuboring "
        "(audio, ovozli xabar yoki hujjat bo'lishi mumkin).\n\n"
        "Bekor qilish uchun /bekor.",
        parse_mode="HTML",
    )
    return WAITING_MUSIC_ADMIN_REPLY


async def cancel_music_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("music_target_uid", None)
    context.user_data.pop("music_target_genre", None)
    context.user_data.pop("music_target_lang", None)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(True))
    return ConversationHandler.END


async def receive_music_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user_id = context.user_data.get("music_target_uid")
    if not target_user_id:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Qaytadan boshlang.", reply_markup=main_menu_keyboard(True)
        )
        return ConversationHandler.END

    msg = update.message
    caption_prefix = "🎵 <b>Sizning musiqangiz tayyor bo'ldi!</b>\n\n"

    # Foydalanuvchidagi "aylanayotgan" animatsiyani to'xtatamiz.
    await _stop_animation(
        target_user_id,
        context.bot,
        final_text="✅ <b>Musiqangiz tayyor bo'ldi!</b>\n\n🎵 Pastda yubordik, tinglang 👇",
    )

    try:
        if msg.audio:
            caption = caption_prefix + (msg.caption or "")
            await context.bot.send_audio(
                chat_id=target_user_id, audio=msg.audio.file_id, caption=caption, parse_mode="HTML"
            )
        elif msg.voice:
            await context.bot.send_message(
                chat_id=target_user_id, text=caption_prefix, parse_mode="HTML"
            )
            await context.bot.send_voice(chat_id=target_user_id, voice=msg.voice.file_id)
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
            "✅ Musiqa foydalanuvchiga muvaffaqiyatli yuborildi!", reply_markup=main_menu_keyboard(True)
        )
    except TelegramError:
        await update.message.reply_text(
            "❌ Yuborishda xatolik yuz berdi (foydalanuvchi botni bloklagan bo'lishi mumkin).",
            reply_markup=main_menu_keyboard(True),
        )

    context.user_data.pop("music_target_uid", None)
    context.user_data.pop("music_target_genre", None)
    context.user_data.pop("music_target_lang", None)
    return ConversationHandler.END
