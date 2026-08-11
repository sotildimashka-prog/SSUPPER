# -*- coding: utf-8 -*-
"""🎵 Musiqa yaratish bo'limi.

Oqim:
1) Foydalanuvchi "🎵 Musiqa yaratish" tugmasini bosadi -> janr tanlash
   (Jazz / Bass / Sokin / Rep) inline tugmalari chiqadi.
2) Janr tanlangach -> til tanlash (bayroqlar bilan: 🇺🇿 🇷🇺 🇸🇦 🇬🇧).
3) Til tanlangach -> "🎧 Musiqa tayyorlash" tugmasi chiqadi.
4) Tugma bosilgach -> 1 dan 100 gacha animatsiya (foiz ko'rinishida) va
   "Musiqa yaratilmoqda, kutib turing..." matni almashinib turadi.
5) Animatsiya tugagach, so'rov to'liq holda ADMIN'ga (@auwsn) yuboriladi,
   admin esa "🎵 Musiqani yuborish" tugmasini bosib tayyor musiqa faylini
   (audio/ovozli xabar/hujjat) yuboradi -> u avtomatik foydalanuvchiga
   yetkaziladi.
"""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError

from config import ADMIN_ID
from keyboards import (
    main_menu_keyboard,
    music_genre_keyboard,
    music_language_keyboard,
    music_prepare_keyboard,
    music_admin_send_keyboard,
    MUSIC_GENRES,
    MUSIC_LANGS,
)
from handlers.subscription import require_subscription

WAITING_MUSIC_ADMIN_REPLY = range(1)[0]

# Animatsiya bosqichlari: avval sekin (1,2,3...) keyin tezroq sakrab 100 gacha.
_PROGRESS_STEPS = [1, 2, 3, 4, 5, 6, 7, 8, 15, 25, 38, 52, 66, 78, 89, 96, 100]

# "Kutib turing" matnini jonli qilish uchun almashinadigan nuqtalar.
_WAIT_DOTS = [".", "..", "...", "...."]


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
# 2) Janr tanlandi -> til tanlash
# ---------------------------------------------------------------------------
async def on_music_genre_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await query.edit_message_text(
        f"✅ Janr: <b>{genre_label}</b>\n"
        f"✅ Til: <b>{lang_label}</b>\n\n"
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
# 4) "Musiqa tayyorlash" bosildi -> animatsiya + adminga yuborish
# ---------------------------------------------------------------------------
async def on_music_prepare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, _, genre, lang = query.data.split(":", 3)
    if genre not in MUSIC_GENRES or lang not in MUSIC_LANGS:
        return

    user = query.from_user
    genre_label, genre_short = MUSIC_GENRES[genre]
    lang_label, lang_short = MUSIC_LANGS[lang]

    # --- Animatsiya: 1 dan 100 gacha "yaratilmoqda" effekti ---
    for i, percent in enumerate(_PROGRESS_STEPS):
        dots = _WAIT_DOTS[i % len(_WAIT_DOTS)]
        bar_filled = round(percent / 10)
        bar = "▓" * bar_filled + "░" * (10 - bar_filled)
        try:
            await query.edit_message_text(
                f"🎶 <b>Musiqa yaratilmoqda, kutib turing{dots}</b>\n\n"
                f"{bar}  <b>{percent}%</b>\n\n"
                f"🎧 Janr: {genre_short}\n"
                f"🌐 Til: {lang_short}",
                parse_mode="HTML",
            )
        except TelegramError:
            pass
        await asyncio.sleep(0.45)

    await query.edit_message_text(
        "✅ <b>So'rovingiz qabul qilindi!</b>\n\n"
        f"🎧 Janr: {genre_short}\n"
        f"🌐 Til: {lang_short}\n\n"
        "🎵 Admin (@auwsn) tez orada tayyor musiqangizni yuboradi.",
        parse_mode="HTML",
    )

    admin_text = (
        "🎵 <b>Yangi MUSIQA YARATISH so'rovi!</b>\n\n"
        f"👤 Foydalanuvchi: {user.first_name or '-'} (@{user.username or '—'})\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n\n"
        f"🎧 Janr: {genre_label}\n"
        f"🌐 Til: {lang_label}"
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
