# -*- coding: utf-8 -*-
"""🟢 OSON O'YINLAR - 20 ta yengil o'yin (12 ta jonli o'yin + 8 ta savol).

Turlari:
  • 🎮 JONLI O'YINLAR (tanlov asosida): tosh-qaychi-qog'oz, tanga, stakan,
    mina, raqam top, katta/kichik, rang top.
  • 🎲 TELEGRAM ANIMATSIYALI O'YINLAR: zar 🎲, darts 🎯, basketbol 🏀,
    futbol ⚽, bouling 🎳 - Telegram'ning haqiqiy animatsiyasi tashlanadi
    va natija shunga qarab hisoblanadi.
  • 🧠 SAVOL-JAVOB o'yinlari (8 ta mavzu, 30 soniya vaqt bilan).

Mukofot tizimi (barcha o'yinlarda bir xil):
  ✅ Yutuq / to'g'ri javob  ->  +3 💎
  ❌ Yutqazish / noto'g'ri javob / vaqt tugashi  ->  −3 💎
  🤝 Durrang (tosh-qaychi-qog'oz) -> almaz o'zgarmaydi, qayta o'ynash mumkin.

Har bir o'yin uchun kutish vaqti ALOHIDA hisoblanadi (bittasini o'ynasangiz
qolgan 19 tasi ochiq qoladi). Callback prefiksi: "eg:..."
"""

import asyncio
import random
import time

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from handlers.message_utils import safe_edit_message

import database as db
from data.easy_questions_data import EASY_QUESTIONS

# 💎 Mukofot va jarima (yutsa +3, yutqazsa −3)
REWARD_AMOUNT = 3
PENALTY_AMOUNT = 3

QUIZ_TIME_LIMIT = 30          # Savol-javob o'yinlariga beriladigan vaqt (soniya)
WARNING_LEAD_SECONDS = 5      # Vaqt tugashiga shuncha soniya qolganda ogohlantirish
PLAY_COOLDOWN_HOURS = 25      # O'yin tugagach FAQAT O'SHA o'yin uchun kutish
TIMEOUT_COOLDOWN_HOURS = 24   # Vaqt tugaganda FAQAT O'SHA o'yin uchun kutish

DICE_WAIT_SECONDS = 4.5       # Telegram animatsiyasi tugashini kutish


# ---------------------------------------------------------------------------
# 20 ta o'yin ro'yxati: key -> (tugma matni, turi)
#   tur: "pick"  - tugma tanlanadigan jonli o'yin
#        "dice"  - Telegram animatsiyali o'yin
#        "quiz"  - savol-javob
# ---------------------------------------------------------------------------

EASY_GAMES = [
    # --- 🎮 Jonli o'yinlar ---
    ("rps",      "✂️ Tosh-qaychi-qog'oz", "pick"),
    ("coin",     "🪙 Tanga tashlash",      "pick"),
    ("cup",      "🥤 Stakan ostidagi to'p", "pick"),
    ("mine",     "💣 Minaga tushma",       "pick"),
    ("guessnum", "🔢 Raqamni top",         "pick"),
    ("highlow",  "🎴 Katta yoki kichik",   "pick"),
    ("color",    "🚦 Rangni top",          "pick"),
    # --- 🎲 Telegram animatsiyali o'yinlar ---
    ("dice",     "🎲 Zar o'yini",          "dice"),
    ("dart",     "🎯 Darts",               "dice"),
    ("basket",   "🏀 Basketbol",           "dice"),
    ("football", "⚽ Futbol (penalti)",    "dice"),
    ("bowling",  "🎳 Bouling",             "dice"),
    # --- 🧠 Savol-javob o'yinlari ---
    ("ffbasic",  "🎮 Free Fire asoslari",  "quiz"),
    ("weapons",  "🔫 Qurollar",            "quiz"),
    ("maps",     "🗺 Xaritalar",           "quiz"),
    ("characters", "🦸 Personajlar",       "quiz"),
    ("math",     "➕ Oson matematika",     "quiz"),
    ("logic",    "💡 Oson mantiq",         "quiz"),
    ("emoji",    "😀 Emoji topishmoq",     "quiz"),
    ("uz",       "🇺🇿 O'zbekiston",        "quiz"),
]

GAME_TITLES = {key: title for key, title, _ in EASY_GAMES}
GAME_TYPES = {key: kind for key, _, kind in EASY_GAMES}


# --- 🎮 Jonli o'yinlar sozlamalari: tanlov tugmalari va qoidasi ---
PICK_GAMES = {
    "rps": {
        "text": "✂️ <b>TOSH - QAYCHI - QOG'OZ</b>\n\nTanlovingizni qiling, men ham tanlayman!",
        "options": [("🪨 Tosh", "0"), ("✂️ Qaychi", "1"), ("📄 Qog'oz", "2")],
    },
    "coin": {
        "text": "🪙 <b>TANGA TASHLASH</b>\n\nTangani havoga otaman — qaysi tomoni tushadi?",
        "options": [("🦅 Burgut", "0"), ("🔢 Raqam", "1")],
    },
    "cup": {
        "text": "🥤 <b>STAKAN OSTIDAGI TO'P</b>\n\nTo'p 3 ta stakandan birining ostida. Qaysi biri?",
        "options": [("1️⃣", "0"), ("2️⃣", "1"), ("3️⃣", "2")],
    },
    "mine": {
        "text": (
            "💣 <b>MINAGA TUSHMA</b>\n\n4 ta katakdan bittasida mina bor.\n"
            "Xavfsiz katakni tanlang — minaga tushmasangiz yutasiz!"
        ),
        "options": [("🟦 1", "0"), ("🟦 2", "1"), ("🟦 3", "2"), ("🟦 4", "3")],
    },
    "guessnum": {
        "text": "🔢 <b>RAQAMNI TOP</b>\n\nMen 1 dan 3 gacha raqam o'yladim. Qaysi biri?",
        "options": [("1️⃣", "0"), ("2️⃣", "1"), ("3️⃣", "2")],
    },
    "highlow": {
        "text": (
            "🎴 <b>KATTA YOKI KICHIK</b>\n\nMen 1 dan 100 gacha son o'yladim.\n"
            "U kichikmi (1-50) yoki kattami (51-100)?"
        ),
        "options": [("🔽 Kichik (1-50)", "0"), ("🔼 Katta (51-100)", "1")],
    },
    "color": {
        "text": "🚦 <b>RANGNI TOP</b>\n\nMen 3 ta rangdan bittasini tanladim. Qaysi biri?",
        "options": [("🔴 Qizil", "0"), ("🟢 Yashil", "1"), ("🔵 Ko'k", "2")],
    },
}

# --- 🎲 Telegram animatsiyali o'yinlar sozlamalari ---
#   emoji        - Telegram dice emojisi
#   win_values   - g'alaba hisoblanadigan natijalar
#   intro        - tashlashdan oldingi matn
#   win_text / lose_text - natija izohi
DICE_GAMES = {
    "dice": {
        "emoji": "🎲",
        "win_values": {4, 5, 6},
        "intro": "🎲 <b>ZAR O'YINI</b>\n\nZarni tashlayman!\n✅ 4, 5 yoki 6 tushsa — yutasiz.\n❌ 1, 2 yoki 3 tushsa — yutqazasiz.",
        "win_text": "🎲 Zarda <b>{v}</b> tushdi — katta son!",
        "lose_text": "🎲 Zarda <b>{v}</b> tushdi — kichik son.",
    },
    "dart": {
        "emoji": "🎯",
        "win_values": {4, 5, 6},
        "intro": "🎯 <b>DARTS</b>\n\nO'q otaman!\n✅ Markazga yaqin tushsa — yutasiz.",
        "win_text": "🎯 Zo'r otish! Markazga urildi!",
        "lose_text": "🎯 O'q chetga ketdi.",
    },
    "basket": {
        "emoji": "🏀",
        "win_values": {4, 5},
        "intro": "🏀 <b>BASKETBOL</b>\n\nTo'pni savatga otaman!\n✅ Savatga tushsa — yutasiz.",
        "win_text": "🏀 To'p savatga tushdi! Ajoyib!",
        "lose_text": "🏀 To'p savatga tushmadi.",
    },
    "football": {
        "emoji": "⚽",
        "win_values": {3, 4, 5},
        "intro": "⚽ <b>PENALTI</b>\n\nDarvozaga zarba beraman!\n✅ Gol bo'lsa — yutasiz.",
        "win_text": "⚽ GOOOL! Darvozaga kirdi!",
        "lose_text": "⚽ Afsus, gol bo'lmadi.",
    },
    "bowling": {
        "emoji": "🎳",
        "win_values": {4, 5, 6},
        "intro": "🎳 <b>BOULING</b>\n\nSharni yumalataman!\n✅ Ko'p kegli yiqilsa — yutasiz.",
        "win_text": "🎳 Zo'r zarba! Keglilar yiqildi!",
        "lose_text": "🎳 Keglilar deyarli qimirlamadi.",
    },
}


def _cd_key(key: str) -> str:
    """Kutish vaqti qiyin o'yinlar bilan chalkashmasligi uchun prefiks."""
    return f"easy:{key}"


INTRO_TEXT = (
    "🟢 <b>OSON O'YINLAR</b>\n\n"
    f"Bu yerda {len(EASY_GAMES)} ta yengil o'yin bor: tosh-qaychi-qog'oz, tanga, "
    "zar 🎲, darts 🎯, basketbol 🏀, futbol ⚽ va qiziqarli savollar! 🎯\n\n"
    f"✅ Yutsangiz — <b>+{REWARD_AMOUNT} 💎</b>\n"
    f"❌ Yutqazsangiz — <b>−{PENALTY_AMOUNT} 💎</b>\n\n"
    "O'yinni tanlang 👇"
)

TIMEOUT_TEXT = f"⏰ Vaqt tugadi! Endi bu o'yinni {TIMEOUT_COOLDOWN_HOURS} soatdan keyin o'ynaysiz."
WARNING_TEXT = "⏰ <b>Vaqtingiz tugayapti, shoshiling!</b>"
PLAYED_TEXT = f"⏳ Bu o'yinni qayta o'ynash uchun {PLAY_COOLDOWN_HOURS} soat kuting."


# ---------------------------------------------------------------------------
# Yordamchilar
# ---------------------------------------------------------------------------

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
    return (time.time() - start_ts) > QUIZ_TIME_LIMIT


def _penalty_suffix(deducted: int) -> str:
    if deducted > 0:
        return f"\n\n💎 <b>-{deducted} Almaz</b> hisobingizdan yechildi."
    return ""


def _reward_suffix() -> str:
    return f"\n\n💎 <b>+{REWARD_AMOUNT} Almaz</b> hisobingizga qo'shildi!"


def _finish_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data="eg:list")]]
    )


async def _win(query, header: str):
    """✅ G'alaba: +REWARD_AMOUNT 💎."""
    db.give_game_reward(_user_id(query), REWARD_AMOUNT)
    await safe_edit_message(
        query,
        f"✅ <b>G'alaba!</b>\n{header}" + _reward_suffix() + f"\n\n{PLAYED_TEXT}",
        reply_markup=_finish_keyboard(),
        parse_mode="HTML",
    )


async def _lose(query, header: str):
    """❌ Yutqazish: −PENALTY_AMOUNT 💎."""
    deducted = db.apply_hard_game_penalty(_user_id(query), PENALTY_AMOUNT)
    await safe_edit_message(
        query,
        f"❌ <b>Yutqazdingiz.</b>\n{header}" + _penalty_suffix(deducted) + f"\n\n{PLAYED_TEXT}",
        reply_markup=_finish_keyboard(),
        parse_mode="HTML",
    )


def _next_question(context: ContextTypes.DEFAULT_TYPE, user_id: int, key: str) -> dict:
    """Savollarni takrorlanmasdan (barchasi chiqmaguncha qayta chiqmaydigan
    tartibda) beradi."""
    pool = EASY_QUESTIONS[key]
    store = context.bot_data.setdefault("easy_games_queues", {})
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


# ---------------------------------------------------------------------------
# Ro'yxat va statistika ekranlari
# ---------------------------------------------------------------------------

def _games_list_keyboard() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for key, title, _kind in EASY_GAMES:
        row.append(InlineKeyboardButton(title, callback_data=f"eg:play:{key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("📊 Bugungi ishlagan almazim", callback_data="eg:stats")])
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="hg:intro")])
    return InlineKeyboardMarkup(rows)


async def show_easy_list(query):
    await safe_edit_message(
        query, INTRO_TEXT, reply_markup=_games_list_keyboard(), parse_mode="HTML"
    )


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
        [[InlineKeyboardButton("⬅️ Orqaga", callback_data="eg:list")]]
    )
    await safe_edit_message(query, text, reply_markup=kb, parse_mode="HTML")


# ---------------------------------------------------------------------------
# ⏰ Savol-javob uchun vaqt ogohlantirishi
# ---------------------------------------------------------------------------

def _warn_job_name(user_id: int, ts: str) -> str:
    return f"eg_warn:{user_id}:{ts}"


def _cancel_warning_job(context, user_id: int, ts: str):
    job_queue = getattr(context, "job_queue", None)
    if job_queue is None:
        return
    for job in job_queue.get_jobs_by_name(_warn_job_name(user_id, ts)):
        job.schedule_removal()


async def _send_time_warning(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    try:
        await context.bot.edit_message_text(
            chat_id=data["chat_id"],
            message_id=data["message_id"],
            text=f"{WARNING_TEXT}\n\n{data['body']}",
            reply_markup=data["reply_markup"],
            parse_mode="HTML",
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# O'yinni ochish
# ---------------------------------------------------------------------------

async def _open_game(query, context, key: str):
    user_id = _user_id(query)
    allowed, remaining = db.check_hard_game_cooldown(user_id, _cd_key(key))
    if not allowed:
        await query.answer(
            f"⏳ Bu o'yinni {_fmt_time(remaining)}dan keyin qayta o'ynashingiz mumkin.",
            show_alert=True,
        )
        return

    db.set_hard_game_cooldown(user_id, _cd_key(key), PLAY_COOLDOWN_HOURS)
    await query.answer()

    kind = GAME_TYPES.get(key)
    if kind == "pick":
        await _open_pick_game(query, key)
    elif kind == "dice":
        await _play_dice_game(query, context, key)
    else:
        await _open_quiz_game(query, context, key)


async def _open_pick_game(query, key: str):
    """🎮 Tanlov asosidagi jonli o'yin (tosh-qaychi-qog'oz, tanga va h.k.)."""
    cfg = PICK_GAMES[key]
    rows = [
        [InlineKeyboardButton(label, callback_data=f"eg:pick:{key}:{val}")]
        for label, val in cfg["options"]
    ]
    rows.append([InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data="eg:list")])
    text = (
        f"{cfg['text']}\n\n"
        f"✅ Yutuq: +{REWARD_AMOUNT} 💎   ❌ Yutqazish: −{PENALTY_AMOUNT} 💎"
    )
    await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="HTML")


async def _open_quiz_game(query, context, key: str):
    """🧠 Savol-javob o'yini (30 soniya vaqt bilan)."""
    user_id = _user_id(query)
    q = _next_question(context, user_id, key)
    correct = q["correct"]
    ts = _new_ts()

    rows = [
        [InlineKeyboardButton(opt, callback_data=f"eg:ans:{key}:{correct}:{i}:{ts}")]
        for i, opt in enumerate(q["options"])
    ]
    rows.append([InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data="eg:list")])
    markup = InlineKeyboardMarkup(rows)

    title = GAME_TITLES.get(key, "🟢 O'yin")
    body = (
        f"{title}\n"
        f"⏱ Vaqt: {QUIZ_TIME_LIMIT} soniya  |  ✅ +{REWARD_AMOUNT} 💎  ❌ −{PENALTY_AMOUNT} 💎\n\n"
        f"{q['question']}"
    )
    await safe_edit_message(query, body, reply_markup=markup, parse_mode="HTML")

    job_queue = getattr(context, "job_queue", None)
    if job_queue is not None and QUIZ_TIME_LIMIT > WARNING_LEAD_SECONDS:
        job_queue.run_once(
            _send_time_warning,
            when=QUIZ_TIME_LIMIT - WARNING_LEAD_SECONDS,
            data={
                "chat_id": query.message.chat_id,
                "message_id": query.message.message_id,
                "body": body,
                "reply_markup": markup,
            },
            name=_warn_job_name(user_id, ts),
        )


# ---------------------------------------------------------------------------
# 🎲 Telegram animatsiyali o'yinlar
# ---------------------------------------------------------------------------

async def _play_dice_game(query, context, key: str):
    """Telegram'ning haqiqiy 🎲/🎯/🏀/⚽/🎳 animatsiyasini yuboradi va
    tushgan natijaga qarab +3 yoki −3 💎 beradi."""
    cfg = DICE_GAMES[key]

    await safe_edit_message(
        query,
        f"{cfg['intro']}\n\n⏳ Tashlanmoqda...",
        reply_markup=None,
        parse_mode="HTML",
    )

    value = None
    try:
        msg = await context.bot.send_dice(
            chat_id=query.message.chat_id, emoji=cfg["emoji"]
        )
        value = msg.dice.value if msg and msg.dice else None
        await asyncio.sleep(DICE_WAIT_SECONDS)
    except TelegramError:
        # Animatsiyani yuborib bo'lmadi - natija baribir adolatli tarzda
        # tasodifiy tanlanadi.
        value = None

    if value is None:
        value = random.randint(1, 6)

    if value in cfg["win_values"]:
        await _win(query, cfg["win_text"].format(v=value))
    else:
        await _lose(query, cfg["lose_text"].format(v=value))


# ---------------------------------------------------------------------------
# 🎮 Tanlov o'yinlarining natijasi
# ---------------------------------------------------------------------------

_RPS_NAMES = ["🪨 Tosh", "✂️ Qaychi", "📄 Qog'oz"]
_COIN_NAMES = ["🦅 Burgut", "🔢 Raqam"]
_COLOR_NAMES = ["🔴 Qizil", "🟢 Yashil", "🔵 Ko'k"]


async def _handle_pick(query, context, key: str, chosen: int):
    await query.answer()

    # --- ✂️ Tosh-qaychi-qog'oz ---
    if key == "rps":
        bot_pick = random.randint(0, 2)
        header = f"Men: {_RPS_NAMES[bot_pick]}  |  Siz: {_RPS_NAMES[chosen]}"
        if bot_pick == chosen:
            # 🤝 Durrang - almaz o'zgarmaydi, o'yin qaytadan ochiladi.
            db.set_hard_game_cooldown(_user_id(query), _cd_key(key), 0)
            await safe_edit_message(
                query,
                f"🤝 <b>Durrang!</b>\n{header}\n\n"
                "💎 Almazingiz o'zgarmadi. Qaytadan urinib ko'ring!",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔄 Qaytadan", callback_data=f"eg:play:{key}")],
                        [InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data="eg:list")],
                    ]
                ),
                parse_mode="HTML",
            )
            return
        # 0=tosh, 1=qaychi, 2=qog'oz -> foydalanuvchi yutadi:
        win = (chosen, bot_pick) in {(0, 1), (1, 2), (2, 0)}
        await (_win(query, header) if win else _lose(query, header))
        return

    # --- 🪙 Tanga ---
    if key == "coin":
        result = random.randint(0, 1)
        header = f"Tanga: {_COIN_NAMES[result]}  |  Siz: {_COIN_NAMES[chosen]}"
        await (_win(query, header) if result == chosen else _lose(query, header))
        return

    # --- 🥤 Stakan ostidagi to'p ---
    if key == "cup":
        result = random.randint(0, 2)
        header = f"To'p <b>{result + 1}-stakan</b> ostida edi. Siz {chosen + 1}-ni tanladingiz."
        await (_win(query, header) if result == chosen else _lose(query, header))
        return

    # --- 💣 Mina ---
    if key == "mine":
        mine = random.randint(0, 3)
        if chosen == mine:
            await _lose(query, f"💥 {mine + 1}-katakda mina bor edi!")
        else:
            await _win(query, f"✔️ {chosen + 1}-katak xavfsiz! Mina {mine + 1}-katakda edi.")
        return

    # --- 🔢 Raqamni top ---
    if key == "guessnum":
        result = random.randint(0, 2)
        header = f"Men <b>{result + 1}</b> raqamini o'ylagandim. Siz {chosen + 1} dedingiz."
        await (_win(query, header) if result == chosen else _lose(query, header))
        return

    # --- 🎴 Katta yoki kichik ---
    if key == "highlow":
        number = random.randint(1, 100)
        actual = 0 if number <= 50 else 1
        header = f"Men o'ylagan son: <b>{number}</b>"
        await (_win(query, header) if actual == chosen else _lose(query, header))
        return

    # --- 🚦 Rangni top ---
    if key == "color":
        result = random.randint(0, 2)
        header = f"Men tanlagan rang: {_COLOR_NAMES[result]}  |  Siz: {_COLOR_NAMES[chosen]}"
        await (_win(query, header) if result == chosen else _lose(query, header))
        return

    await query.answer()


# ---------------------------------------------------------------------------
# 🧠 Savol-javob natijasi
# ---------------------------------------------------------------------------

async def _handle_timeout(query, context, key: str):
    deducted = db.apply_hard_game_penalty(_user_id(query), PENALTY_AMOUNT)
    db.set_hard_game_cooldown(_user_id(query), _cd_key(key), TIMEOUT_COOLDOWN_HOURS)
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
# Callback router ("eg:...")
# ---------------------------------------------------------------------------

async def on_easy_games_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha "eg:..." callbacklarini boshqaradi."""
    query = update.callback_query
    parts = query.data.split(":")

    try:
        action = parts[1]

        if action == "list":
            await query.answer()
            await show_easy_list(query)
            return

        if action == "stats":
            await query.answer()
            await _show_stats(query)
            return

        if action == "play":
            key = parts[2]
            if key not in GAME_TYPES:
                await query.answer()
                return
            await _open_game(query, context, key)
            return

        if action == "pick":
            key, chosen = parts[2], int(parts[3])
            if key not in PICK_GAMES:
                await query.answer()
                return
            await _handle_pick(query, context, key, chosen)
            return

        if action == "ans":
            key, correct, chosen, ts = parts[2], int(parts[3]), int(parts[4]), parts[5]
            await _handle_answer(query, context, key, correct, chosen, ts)
            return

        await query.answer()
    except (IndexError, ValueError):
        await query.answer("⚠️ Xatolik. Qaytadan urinib ko'ring.", show_alert=True)
