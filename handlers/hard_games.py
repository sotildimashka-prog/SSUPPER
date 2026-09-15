# -*- coding: utf-8 -*-
"""🎮 MINI O'YINLAR - Qiyin darajadagi 10 ta Free Fire o'yini.

Oqim:
  1. "🎮 Mini O'yinlar" tugmasi bosiladi -> qoida matni + "🚀 BOSHLASH" tugmasi.
  2. "BOSHLASH" bosilganda 10 ta qiyin o'yin ro'yxati + "📊 Bugungi ishlagan
     almazim" tugmasi chiqadi.
  3. O'yinlardan biri tanlansa - 25 soniya ichida javob berish kerak bo'lgan
     qiyin Free Fire savoli chiqadi.
       - To'g'ri va vaqtida javob berilsa -> +3 💎, 25 soatlik umumiy kutish.
       - Noto'g'ri javob yoki vaqt tugasa -> -3 💎 (bor bo'lsa).
       - Vaqt tugagan holatda alohida xabar va 24 soatlik kutish ko'rsatiladi.
  4. "📊 Bugungi ishlagan almazim" - foydalanuvchining bugungi haqiqiy
     statistikasini ko'rsatadi (ishlagan / minus bo'lgan / natija).
"""

import random
import time

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from handlers.message_utils import safe_edit_message

import database as db
from data.hard_questions_data import HARD_QUESTIONS

REWARD_AMOUNT = 3
PENALTY_AMOUNT = 3

GAME_TIME_LIMIT = 25          # Har bir savolga javob berish uchun vaqt (soniya)
PLAY_COOLDOWN_HOURS = 25      # O'yin muvaffaqiyatli tugagach keyingisi uchun kutish
TIMEOUT_COOLDOWN_HOURS = 24   # Vaqt tugab ketganda keyingisi uchun kutish

HARD_GAMES = [
    ("puzzle", "🧩 Mantiqiy jumboq"),
    ("riddle", "🧠 Topishmoq"),
    ("numbers", "🔢 Sonlar jumbog'i"),
    ("detective", "🕵️ Detektiv savol"),
    ("ffquiz", "🔥 Free Fire viktorinasi"),
    ("fast", "⚡ Tezkor savol"),
    ("hidden", "🎯 Yashirin javob"),
    ("code", "🔐 Kodni top"),
    ("trap", "🧩 Mantiqiy tuzoq"),
    ("superquiz", "🏆 Free Fire super viktorinasi"),
]
HARD_GAME_TITLES = dict(HARD_GAMES)

INTRO_TEXT = (
    "🎮 <b>MINI O'YINLAR</b>\n\n"
    "Mini o'yinlar orqali 💎 almaz ishlab olishingiz mumkin.\n"
    f"⚠️ Yutsangiz +{REWARD_AMOUNT} 💎, topa olmasangiz −{PENALTY_AMOUNT} 💎.\n\n"
    "Agar rozi bo'lsangiz, BOSHLASH tugmasini bosing."
)

TIMEOUT_TEXT = "⏰ Vaqt tugadi! Endi yana 24 soat kutasiz."
PLAYED_TEXT = "🎮 Siz o'yinni o'ynadingiz!\n⏳ Keyingi o'yinni o'ynash uchun 25 soat kuting."


def _fmt_time(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0:
        return f"{h} soat {m} daqiqa"
    return f"{m} daqiqa"


def _user_id(query) -> int:
    return query.from_user.id


def _new_ts() -> str:
    return f"{time.time():.2f}"


def _is_expired(start_ts_str: str) -> bool:
    try:
        start_ts = float(start_ts_str)
    except (TypeError, ValueError):
        return False
    return (time.time() - start_ts) > GAME_TIME_LIMIT


def _penalty_suffix(deducted: int) -> str:
    if deducted > 0:
        return f"\n\n💎 <b>-{deducted} Almaz</b> hisobingizdan yechildi."
    return ""


def _next_question(context: ContextTypes.DEFAULT_TYPE, user_id: int, key: str) -> dict:
    """Har bir kategoriya bo'yicha savollarni takrorlanmasdan (barchasi bir
    marta chiqmaguncha qayta chiqmaydigan tartibda) beradi."""
    pool = HARD_QUESTIONS[key]
    store = context.bot_data.setdefault("hard_games_queues", {})
    state = store.setdefault(user_id, {})
    queue = state.get(key)

    if not queue:
        indices = list(range(len(pool)))
        random.shuffle(indices)
        last_idx = state.get(f"{key}:last")
        if last_idx is not None and indices and indices[0] == last_idx and len(indices) > 1:
            indices[0], indices[1] = indices[1], indices[0]
        queue = indices

    idx = queue.pop(0)
    state[key] = queue
    state[f"{key}:last"] = idx
    return pool[idx]


def _games_list_keyboard() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for key, title in HARD_GAMES:
        row.append(InlineKeyboardButton(title, callback_data=f"hg:play:{key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("📊 Bugungi ishlagan almazim", callback_data="hg:stats")])
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="hg:intro")])
    return InlineKeyboardMarkup(rows)


def _games_list_text() -> str:
    return (
        "🎮 <b>MINI O'YINLAR</b>\n\n"
        f"⚠️ Yutsangiz +{REWARD_AMOUNT} 💎, topa olmasangiz −{PENALTY_AMOUNT} 💎.\n"
        f"⏱ Har bir o'yinga {GAME_TIME_LIMIT} soniya vaqt beriladi.\n\n"
        "O'yinni tanlang:"
    )


# ---------------------------------------------------------------------------
# Kirish nuqtalari
# ---------------------------------------------------------------------------

def _intro_keyboard() -> InlineKeyboardMarkup:
    """🚀 BOSHLASH + 💎 Almaz ishlash menyusiga qaytish tugmasi.
    Bu bo'lim endi faqat 💎 Almaz ishlash -> 🎮 O'yinlar tugmasi orqali
    ochiladi, shu sabab "Ortga" doim o'sha menyuga qaytaradi."""
    from keyboards import ALMAZ_ISHLASH_CB

    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🚀 BOSHLASH", callback_data="hg:list")],
            [InlineKeyboardButton("🔙 Ortga", callback_data=ALMAZ_ISHLASH_CB)],
        ]
    )


async def on_games_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎮 Mini O'yinlar (Reply tugma bosilganda)."""
    await update.message.reply_text(INTRO_TEXT, reply_markup=_intro_keyboard(), parse_mode="HTML")


async def _show_intro(query):
    await safe_edit_message(query, INTRO_TEXT, reply_markup=_intro_keyboard(), parse_mode="HTML")


async def _show_games_list(query):
    await safe_edit_message(query, _games_list_text(), reply_markup=_games_list_keyboard(), parse_mode="HTML")


async def _show_stats(query):
    user_id = _user_id(query)
    earned = db.get_diamonds_earned_today(user_id)
    lost = db.get_diamonds_lost_today(user_id)
    result = earned - lost
    text = (
        "📊 <b>BUGUNGI ISHLAGAN ALMAZIM</b>\n\n"
        f"💎 Bugun ishlab olgan: +{earned} 💎\n"
        f"❌ Bugun minus bo'lgan: −{lost} 💎\n"
        f"📊 Bugungi natija: {result} 💎"
    )
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Orqaga", callback_data="hg:list")]]
    )
    await safe_edit_message(query, text, reply_markup=kb, parse_mode="HTML")


async def _open_game(query, context, key: str):
    allowed, remaining = db.check_hard_game_cooldown(_user_id(query))
    if not allowed:
        await query.answer(
            f"⏳ Keyingi o'yinni {_fmt_time(remaining)}dan keyin o'ynashingiz mumkin.",
            show_alert=True,
        )
        return

    db.set_hard_game_cooldown(_user_id(query), PLAY_COOLDOWN_HOURS)
    await query.answer()

    q = _next_question(context, _user_id(query), key)
    correct = q["correct"]
    options = q["options"]
    ts = _new_ts()

    rows = [
        [InlineKeyboardButton(opt, callback_data=f"hg:ans:{key}:{correct}:{i}:{ts}")]
        for i, opt in enumerate(options)
    ]
    rows.append([InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data="hg:list")])

    title = HARD_GAME_TITLES.get(key, "🎮 O'yin")
    await safe_edit_message(
        query,
        f"{title}\n⏱ Vaqt: {GAME_TIME_LIMIT} soniya\n\n{q['question']}",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="HTML",
    )


def _finish_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data="hg:list")]]
    )


async def _handle_timeout(query):
    """25 soniyadan kech javob berilganda - jarima qo'llanadi va o'ziga xos
    24 soatlik kutish xabari ko'rsatiladi."""
    deducted = db.apply_hard_game_penalty(_user_id(query), PENALTY_AMOUNT)
    db.set_hard_game_cooldown(_user_id(query), TIMEOUT_COOLDOWN_HOURS)
    await safe_edit_message(
        query,
        TIMEOUT_TEXT + _penalty_suffix(deducted),
        reply_markup=_finish_keyboard(),
        parse_mode="HTML",
    )


async def _handle_answer(query, context, key: str, correct: int, chosen: int, ts: str):
    await query.answer()

    if _is_expired(ts):
        await _handle_timeout(query)
        return

    if chosen == correct:
        db.give_game_reward(_user_id(query), REWARD_AMOUNT)
        text = f"✅ <b>To'g'ri javob!</b>\n💎 +{REWARD_AMOUNT} Almaz qo'shildi!\n\n{PLAYED_TEXT}"
    else:
        deducted = db.apply_hard_game_penalty(_user_id(query), PENALTY_AMOUNT)
        text = "❌ <b>Noto'g'ri javob.</b>" + _penalty_suffix(deducted) + f"\n\n{PLAYED_TEXT}"

    await safe_edit_message(query, text, reply_markup=_finish_keyboard(), parse_mode="HTML")


# ---------------------------------------------------------------------------
# Callback router
# ---------------------------------------------------------------------------

async def on_games_root_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha "hg:..." callbacklarini boshqaradi."""
    query = update.callback_query
    parts = query.data.split(":")

    try:
        action = parts[1]

        if action == "intro":
            await query.answer()
            await _show_intro(query)
            return

        if action == "list":
            await query.answer()
            await _show_games_list(query)
            return

        if action == "stats":
            await query.answer()
            await _show_stats(query)
            return

        if action == "play":
            key = parts[2]
            if key not in HARD_QUESTIONS:
                await query.answer()
                return
            await _open_game(query, context, key)
            return

        if action == "ans":
            key, correct, chosen, ts = parts[2], int(parts[3]), int(parts[4]), parts[5]
            await _handle_answer(query, context, key, correct, chosen, ts)
            return

        await query.answer()
    except (IndexError, ValueError):
        await query.answer("⚠️ Xatolik. Qaytadan urinib ko'ring.", show_alert=True)
