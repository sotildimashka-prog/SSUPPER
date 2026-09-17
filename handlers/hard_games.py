# -*- coding: utf-8 -*-
"""🎮 MINI O'YINLAR - Qiyin darajadagi 10 ta Free Fire o'yini.

Oqim:
  1. "🎮 Mini O'yinlar" tugmasi bosiladi -> qoida matni + "🚀 BOSHLASH" tugmasi.
  2. "BOSHLASH" bosilganda 10 ta qiyin o'yin ro'yxati + "📊 Bugungi ishlagan
     almazim" tugmasi chiqadi.
  3. O'yinlardan biri tanlansa - 30 soniya ichida javob berish kerak bo'lgan
     qiyin Free Fire savoli chiqadi (tugashiga 5 soniya qolganda avtomatik
     "Vaqtingiz tugayapti, shoshiling!" ogohlantirishi chiqadi).
       - To'g'ri va vaqtida javob berilsa -> +3 💎, FAQAT O'SHA o'yin uchun
         25 soatlik kutish (qolgan 9 ta o'yinga tegmaydi).
       - Noto'g'ri javob yoki vaqt tugasa -> -3 💎 (bor bo'lsa).
       - Vaqt tugagan holatda alohida xabar va FAQAT O'SHA o'yin uchun
         24 soatlik kutish ko'rsatiladi.
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

GAME_TIME_LIMIT = 30          # Har bir savolga javob berish uchun vaqt (soniya)
WARNING_LEAD_SECONDS = 5      # Vaqt tugashiga shuncha soniya qolganda ogohlantirish yuboriladi
PLAY_COOLDOWN_HOURS = 25      # O'yin muvaffaqiyatli tugagach FAQAT O'SHA o'yin uchun kutish
TIMEOUT_COOLDOWN_HOURS = 24   # Vaqt tugab ketganda FAQAT O'SHA o'yin uchun kutish

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
    "👋 <b>Assalomu alaykum!</b>\n\n"
    "🎮 <b>MINI O'YINLAR</b> bo'limiga xush kelibsiz!\n\n"
    "Bu yerda qiziqarli va qiyin savollarga javob berib, 💎 almaz ishlab "
    "olishingiz mumkin.\n\n"
    f"⚠️ To'g'ri javob bersangiz +{REWARD_AMOUNT} 💎, noto'g'ri javob "
    f"bersangiz yoki vaqtida ulgurmasangiz −{PENALTY_AMOUNT} 💎 yechiladi.\n"
    f"⏱ Har bir savolga {GAME_TIME_LIMIT} soniya vaqt beriladi.\n\n"
    "🟢 <b>Oson o'yinlar</b> — 20 ta: tosh-qaychi-qog'oz, tanga, zar 🎲, darts 🎯, futbol ⚽ va savollar\n"
    "🔥 <b>Qiyin o'yinlar</b> — 10 ta murakkab Free Fire o'yini\n\n"
    "Darajani tanlang 👇"
)

TIMEOUT_TEXT = f"⏰ Vaqt tugadi! Endi yana {TIMEOUT_COOLDOWN_HOURS} soat kutasiz."
WARNING_TEXT = "⏰ <b>Vaqtingiz tugayapti, shoshiling!</b>"
PLAYED_TEXT = f"🎮 Siz o'yinni o'ynadingiz!\n⏳ Keyingi o'yinni o'ynash uchun {PLAY_COOLDOWN_HOURS} soat kuting."


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
            [
                InlineKeyboardButton("🟢 Oson o'yinlar", callback_data="eg:list"),
                InlineKeyboardButton("🔥 Qiyin o'yinlar", callback_data="hg:list"),
            ],
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


def _warn_job_name(user_id: int, ts: str) -> str:
    return f"hg_warn:{user_id}:{ts}"


def _cancel_warning_job(context, user_id: int, ts: str):
    """Foydalanuvchi javob berganda (yoki vaqt allaqachon tugab, timeout
    ishlanganda) rejalashtirilgan "shoshiling" ogohlantirishini bekor
    qiladi - shu bilan javob berilgan xabarni ortiqcha tahrirlamaydi."""
    job_queue = getattr(context, "job_queue", None)
    if job_queue is None:
        return
    for job in job_queue.get_jobs_by_name(_warn_job_name(user_id, ts)):
        job.schedule_removal()


async def _send_time_warning(context: ContextTypes.DEFAULT_TYPE):
    """Vaqt tugashiga WARNING_LEAD_SECONDS soniya qolganda avtomatik
    ishga tushadi va savol xabariga "Vaqtingiz tugayapti, shoshiling!"
    ogohlantirishini qo'shib qo'yadi (tugmalar o'zgarmaydi)."""
    job = context.job
    data = job.data
    try:
        await context.bot.edit_message_text(
            chat_id=data["chat_id"],
            message_id=data["message_id"],
            text=f"{WARNING_TEXT}\n\n{data['body']}",
            reply_markup=data["reply_markup"],
            parse_mode="HTML",
        )
    except Exception:
        # Xabar allaqachon o'zgargan/o'chirilgan bo'lishi mumkin - jim o'tkaziladi.
        pass


async def _open_game(query, context, key: str):
    user_id = _user_id(query)
    allowed, remaining = db.check_hard_game_cooldown(user_id, key)
    if not allowed:
        await query.answer(
            f"⏳ Bu o'yinni {_fmt_time(remaining)}dan keyin qayta o'ynashingiz mumkin.",
            show_alert=True,
        )
        return

    db.set_hard_game_cooldown(user_id, key, PLAY_COOLDOWN_HOURS)
    await query.answer()

    q = _next_question(context, user_id, key)
    correct = q["correct"]
    options = q["options"]
    ts = _new_ts()

    rows = [
        [InlineKeyboardButton(opt, callback_data=f"hg:ans:{key}:{correct}:{i}:{ts}")]
        for i, opt in enumerate(options)
    ]
    rows.append([InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data="hg:list")])
    markup = InlineKeyboardMarkup(rows)

    title = HARD_GAME_TITLES.get(key, "🎮 O'yin")
    body = f"{title}\n⏱ Vaqt: {GAME_TIME_LIMIT} soniya\n\n{q['question']}"
    await safe_edit_message(query, body, reply_markup=markup, parse_mode="HTML")

    # ⏰ Vaqt tugashiga WARNING_LEAD_SECONDS soniya qolganda avtomatik
    # "shoshiling" ogohlantirishini yuborish uchun job rejalashtiriladi.
    job_queue = getattr(context, "job_queue", None)
    if job_queue is not None and GAME_TIME_LIMIT > WARNING_LEAD_SECONDS:
        job_queue.run_once(
            _send_time_warning,
            when=GAME_TIME_LIMIT - WARNING_LEAD_SECONDS,
            data={
                "chat_id": query.message.chat_id,
                "message_id": query.message.message_id,
                "body": body,
                "reply_markup": markup,
            },
            name=_warn_job_name(user_id, ts),
        )


def _finish_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data="hg:list")]]
    )


async def _handle_timeout(query, context, key: str):
    """GAME_TIME_LIMIT soniyadan kech javob berilganda - jarima qo'llanadi
    va FAQAT shu o'yin (key) uchun TIMEOUT_COOLDOWN_HOURS soatlik kutish
    o'rnatiladi (qolgan o'yinlarga tegmaydi)."""
    deducted = db.apply_hard_game_penalty(_user_id(query), PENALTY_AMOUNT)
    db.set_hard_game_cooldown(_user_id(query), key, TIMEOUT_COOLDOWN_HOURS)
    await safe_edit_message(
        query,
        TIMEOUT_TEXT + _penalty_suffix(deducted),
        reply_markup=_finish_keyboard(),
        parse_mode="HTML",
    )


async def _handle_answer(query, context, key: str, correct: int, chosen: int, ts: str):
    await query.answer()
    _cancel_warning_job(context, _user_id(query), ts)

    if _is_expired(ts):
        await _handle_timeout(query, context, key)
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
