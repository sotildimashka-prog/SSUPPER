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

📈 DARAJA TIZIMI: hisobdagi 💎 ko'paygan sari o'yinlar qiyinlashadi
(100+ 💎 -> 🟡 O'rtacha, 300+ 💎 -> 🔴 Qiyin). Chegaralar va parametrlar
TIER_* / PICK_TIER_PARAMS / DICE_GAMES / QUIZ_TIME_BY_TIER da.

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


# --- 📈 Daraja tizimi ---------------------------------------------------
# Hisobdagi 💎 miqdori ko'payganda o'yinlar qiyinlashadi:
#   0 .. TIER_MEDIUM_FROM-1   -> 🟢 Oson      (avvalgi qoidalar)
#   TIER_MEDIUM_FROM ..       -> 🟡 O'rtacha
#   TIER_HARD_FROM ..         -> 🔴 Qiyin
# Daraja o'yin OCHILGAN paytdagi balansga qarab aniqlanadi va foydalanuvchiga
# doim ko'rsatiladi (ro'yxatda ham, o'yin ekranida ham, ehtimol bilan birga).
TIER_MEDIUM_FROM = 100
TIER_HARD_FROM = 300
TIER_NAMES = ["🟢 Oson", "🟡 O'rtacha", "🔴 Qiyin"]
MAX_TIER = 2
QUIZ_TIME_BY_TIER = [30, 20, 12]   # savol-javob o'yinlarida vaqt (soniya)


def _tier_for_balance(diamonds: int) -> int:
    if diamonds >= TIER_HARD_FROM:
        return 2
    if diamonds >= TIER_MEDIUM_FROM:
        return 1
    return 0


def _user_tier(user_id: int) -> int:
    return _tier_for_balance(db.get_quiz_diamonds(user_id))


def _safe_tier(raw) -> int:
    """callback_data ichidagi darajani xavfsiz o'qiydi (eski tugmalarda yo'q -> 0)."""
    try:
        return max(0, min(MAX_TIER, int(raw)))
    except (TypeError, ValueError):
        return 0


# --- 🎮 Jonli o'yinlar: har bir daraja uchun parametrlar ---
#   cup      - stakanlar soni
#   mine     - (kataklar soni, minalar soni)
#   guessnum - raqamlar soni (1..N)
#   color    - ranglar soni
#   highlow  - 1..100 nechta oraliqqa bo'linadi
#   coin     - tashlanadigan tangalar soni (hammasini topish kerak)
PICK_TIER_PARAMS = {
    "cup":      [3, 4, 5],
    "mine":     [(4, 1), (5, 3), (6, 5)],
    "guessnum": [3, 5, 8],
    "color":    [3, 4, 6],
    "highlow":  [2, 4, 5],
    "coin":     [1, 2, 3],
}
PICK_KEYS = {"rps", "coin", "cup", "mine", "guessnum", "highlow", "color"}

_NUM_EMOJI = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
_RPS_NAMES = ["🪨 Tosh", "✂️ Qaychi", "📄 Qog'oz"]
_COIN_SYMBOLS = ["🦅", "🔢"]  # 0 - burgut, 1 - raqam
_COLOR_POOL = ["🔴 Qizil", "🟢 Yashil", "🔵 Ko'k", "🟡 Sariq", "🟣 Binafsha", "🟠 To'q sariq"]


def _coin_combo(index: int, coins: int) -> str:
    bits = [(index >> (coins - 1 - k)) & 1 for k in range(coins)]
    return "".join(_COIN_SYMBOLS[b] for b in bits)


def _highlow_buckets(n: int) -> list:
    size = 100 // n
    return [(k * size + 1, 100 if k == n - 1 else (k + 1) * size) for k in range(n)]


def _pick_win_percent(key: str, tier: int) -> int:
    """Foydalanuvchiga ko'rsatiladigan yutish ehtimoli (foizda, yaxlitlangan)."""
    if key == "rps":
        return 33
    if key == "mine":
        cells, mines = PICK_TIER_PARAMS["mine"][tier]
        return round((cells - mines) / cells * 100)
    n = PICK_TIER_PARAMS[key][tier]
    if key == "coin":
        return round(100 / (2 ** n))
    return round(100 / n)


def _pick_config(key: str, tier: int):
    """(matn, [(tugma matni, qiymat), ...]) - tanlangan daraja qoidalari bilan."""
    if key == "rps":
        text = "✂️ <b>TOSH - QAYCHI - QOG'OZ</b>\n\nTanlovingizni qiling, men ham tanlayman!"
        if tier > 0:
            text += "\n⚠️ Durrang bo'lsa — yutqazdingiz hisoblanadi!"
        return text, [("🪨 Tosh", "0"), ("✂️ Qaychi", "1"), ("📄 Qog'oz", "2")]

    if key == "coin":
        coins = PICK_TIER_PARAMS["coin"][tier]
        if coins == 1:
            text = "🪙 <b>TANGA TASHLASH</b>\n\nTangani havoga otaman — qaysi tomoni tushadi?"
            return text, [("🦅 Burgut", "0"), ("🔢 Raqam", "1")]
        text = (
            f"🪙 <b>TANGA TASHLASH</b>\n\n{coins} ta tanga havoga otiladi.\n"
            "Ularning tushish tartibini to'liq toping! (🦅 burgut, 🔢 raqam)"
        )
        return text, [(_coin_combo(i, coins), str(i)) for i in range(2 ** coins)]

    if key == "cup":
        n = PICK_TIER_PARAMS["cup"][tier]
        text = f"🥤 <b>STAKAN OSTIDAGI TO'P</b>\n\nTo'p {n} ta stakandan birining ostida. Qaysi biri?"
        return text, [(_NUM_EMOJI[i], str(i)) for i in range(n)]

    if key == "mine":
        cells, mines = PICK_TIER_PARAMS["mine"][tier]
        text = (
            f"💣 <b>MINAGA TUSHMA</b>\n\n{cells} ta katakdan {mines} tasida mina bor.\n"
            "Xavfsiz katakni tanlang — minaga tushmasangiz yutasiz!"
        )
        return text, [(f"🟦 {i + 1}", str(i)) for i in range(cells)]

    if key == "guessnum":
        n = PICK_TIER_PARAMS["guessnum"][tier]
        text = f"🔢 <b>RAQAMNI TOP</b>\n\nMen 1 dan {n} gacha raqam o'yladim. Qaysi biri?"
        return text, [(_NUM_EMOJI[i], str(i)) for i in range(n)]

    if key == "highlow":
        n = PICK_TIER_PARAMS["highlow"][tier]
        buckets = _highlow_buckets(n)
        text = (
            "🎴 <b>KATTA YOKI KICHIK</b>\n\nMen 1 dan 100 gacha son o'yladim.\n"
            "U qaysi oraliqda?"
        )
        return text, [(f"{lo}–{hi}", str(i)) for i, (lo, hi) in enumerate(buckets)]

    if key == "color":
        n = PICK_TIER_PARAMS["color"][tier]
        text = f"🚦 <b>RANGNI TOP</b>\n\nMen {n} ta rangdan bittasini tanladim. Qaysi biri?"
        return text, [(_COLOR_POOL[i], str(i)) for i in range(n)]

    raise KeyError(key)


# --- 🎲 Telegram animatsiyali o'yinlar sozlamalari ---
#   emoji     - Telegram dice emojisi
#   max       - animatsiya beradigan eng katta qiymat
#   head      - tashlashdan oldingi sarlavha
#   hint      - "yutuq" sharti (oson darajada)
#   tiers     - har bir daraja uchun (g'alaba qiymatlari, tashlashlar soni);
#               tashlashlar soni > 1 bo'lsa, HAMMASI yutuq bo'lishi kerak.
DICE_GAMES = {
    "dice": {
        "emoji": "🎲", "max": 6,
        "head": "🎲 <b>ZAR O'YINI</b>\n\nZarni tashlayman!",
        "hint": "Katta son tushsa",
        "tiers": [({4, 5, 6}, 1), ({5, 6}, 1), ({6}, 1)],
        "win_text": "🎲 Zarda <b>{v}</b> tushdi — katta son!",
        "lose_text": "🎲 Zarda <b>{v}</b> tushdi — kichik son.",
    },
    "dart": {
        "emoji": "🎯", "max": 6,
        "head": "🎯 <b>DARTS</b>\n\nO'q otaman!",
        "hint": "Markazga yaqin tushsa",
        "tiers": [({4, 5, 6}, 1), ({5, 6}, 1), ({6}, 1)],
        "win_text": "🎯 Zo'r otish! Markazga urildi!",
        "lose_text": "🎯 O'q chetga ketdi.",
    },
    "basket": {
        "emoji": "🏀", "max": 5,
        "head": "🏀 <b>BASKETBOL</b>\n\nTo'pni savatga otaman!",
        "hint": "Savatga tushsa",
        "tiers": [({4, 5}, 1), ({5}, 1), ({4, 5}, 2)],
        "win_text": "🏀 To'p savatga tushdi! Ajoyib!",
        "lose_text": "🏀 To'p savatga tushmadi.",
    },
    "football": {
        "emoji": "⚽", "max": 5,
        "head": "⚽ <b>PENALTI</b>\n\nDarvozaga zarba beraman!",
        "hint": "Gol bo'lsa",
        "tiers": [({3, 4, 5}, 1), ({4, 5}, 1), ({5}, 1)],
        "win_text": "⚽ GOOOL! Darvozaga kirdi!",
        "lose_text": "⚽ Afsus, gol bo'lmadi.",
    },
    "bowling": {
        "emoji": "🎳", "max": 6,
        "head": "🎳 <b>BOULING</b>\n\nSharni yumalataman!",
        "hint": "Ko'p kegli yiqilsa",
        "tiers": [({4, 5, 6}, 1), ({5, 6}, 1), ({6}, 1)],
        "win_text": "🎳 Zo'r zarba! Keglilar yiqildi!",
        "lose_text": "🎳 Keglilar deyarli qimirlamadi.",
    },
}


def _dice_win_percent(key: str, tier: int) -> int:
    cfg = DICE_GAMES[key]
    values, throws = cfg["tiers"][tier]
    return round(((len(values) / cfg["max"]) ** throws) * 100)


def _dice_rules(key: str, tier: int) -> str:
    cfg = DICE_GAMES[key]
    values, throws = cfg["tiers"][tier]
    if key == "dice":
        vals = ", ".join(str(v) for v in sorted(values))
        line = f"✅ {vals} tushsa — yutasiz.\n❌ Qolgan sonlar — yutqazasiz."
    elif tier == 0:
        line = f"✅ {cfg['hint']} — yutasiz."
    else:
        line = f"✅ {cfg['hint']} (faqat eng yaxshi natijalar hisoblanadi) — yutasiz."
    if throws > 1:
        line += f"\n🔁 {throws} marta tashlanadi — HAMMASI yutuq bo'lishi shart."
    line += f"\n🎯 Taxminiy yutish ehtimoli: ~{_dice_win_percent(key, tier)}%"
    return line


def _cd_key(key: str) -> str:
    """Kutish vaqti qiyin o'yinlar bilan chalkashmasligi uchun prefiks."""
    return f"easy:{key}"


INTRO_TEXT = (
    "🟢 <b>OSON O'YINLAR</b>\n\n"
    f"Bu yerda {len(EASY_GAMES)} ta yengil o'yin bor: tosh-qaychi-qog'oz, tanga, "
    "zar 🎲, darts 🎯, basketbol 🏀, futbol ⚽ va qiziqarli savollar! 🎯\n\n"
    f"✅ Yutsangiz — <b>+{REWARD_AMOUNT} 💎</b>\n"
    f"❌ Yutqazsangiz — <b>−{PENALTY_AMOUNT} 💎</b>"
)


def _intro_text(user_id: int) -> str:
    diamonds = db.get_quiz_diamonds(user_id)
    tier = _tier_for_balance(diamonds)
    return (
        INTRO_TEXT
        + f"\n\n📈 <b>Sizning darajangiz:</b> {TIER_NAMES[tier]} (hisobingizda {diamonds} 💎)\n"
        f"ℹ️ Almazingiz ko'paygan sari o'yinlar qiyinlashadi: "
        f"{TIER_MEDIUM_FROM}+ 💎 — 🟡 O'rtacha, {TIER_HARD_FROM}+ 💎 — 🔴 Qiyin. "
        "Har bir o'yin ekranida yutish ehtimoli ko'rsatiladi.\n\n"
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


def _is_expired(start_ts_str: str, limit: int = QUIZ_TIME_LIMIT) -> bool:
    try:
        start_ts = float(start_ts_str)
    except (TypeError, ValueError):
        return False
    return (time.time() - start_ts) > limit


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
        query, _intro_text(_user_id(query)), reply_markup=_games_list_keyboard(), parse_mode="HTML"
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

    # 📈 Daraja o'yin ochilgan paytdagi balansga qarab aniqlanadi.
    tier = _user_tier(user_id)

    kind = GAME_TYPES.get(key)
    if kind == "pick":
        await _open_pick_game(query, key, tier)
    elif kind == "dice":
        await _play_dice_game(query, context, key, tier)
    else:
        await _open_quiz_game(query, context, key, tier)


async def _open_pick_game(query, key: str, tier: int):
    """🎮 Tanlov asosidagi jonli o'yin (tosh-qaychi-qog'oz, tanga va h.k.)."""
    text_body, options = _pick_config(key, tier)

    # Tugmalarni chiroyli qatorlarga bo'lamiz.
    n = len(options)
    per_row = 1 if n <= 3 else (2 if n <= 6 else 4)
    rows, row = [], []
    for label, val in options:
        row.append(InlineKeyboardButton(label, callback_data=f"eg:pick:{key}:{val}:{tier}"))
        if len(row) == per_row:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data="eg:list")])

    text = (
        f"{text_body}\n\n"
        f"📈 Daraja: {TIER_NAMES[tier]}   🎯 Yutish ehtimoli: ~{_pick_win_percent(key, tier)}%\n"
        f"✅ Yutuq: +{REWARD_AMOUNT} 💎   ❌ Yutqazish: −{PENALTY_AMOUNT} 💎"
    )
    await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="HTML")


async def _open_quiz_game(query, context, key: str, tier: int):
    """🧠 Savol-javob o'yini (vaqt darajaga qarab: 30 / 20 / 12 soniya)."""
    user_id = _user_id(query)
    limit = QUIZ_TIME_BY_TIER[tier]
    q = _next_question(context, user_id, key)
    correct = q["correct"]
    ts = _new_ts()

    rows = [
        [InlineKeyboardButton(opt, callback_data=f"eg:ans:{key}:{correct}:{i}:{ts}:{limit}")]
        for i, opt in enumerate(q["options"])
    ]
    rows.append([InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data="eg:list")])
    markup = InlineKeyboardMarkup(rows)

    title = GAME_TITLES.get(key, "🟢 O'yin")
    body = (
        f"{title}\n"
        f"📈 Daraja: {TIER_NAMES[tier]}\n"
        f"⏱ Vaqt: {limit} soniya  |  ✅ +{REWARD_AMOUNT} 💎  ❌ −{PENALTY_AMOUNT} 💎\n\n"
        f"{q['question']}"
    )
    await safe_edit_message(query, body, reply_markup=markup, parse_mode="HTML")

    job_queue = getattr(context, "job_queue", None)
    if job_queue is not None and limit > WARNING_LEAD_SECONDS:
        job_queue.run_once(
            _send_time_warning,
            when=limit - WARNING_LEAD_SECONDS,
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

async def _play_dice_game(query, context, key: str, tier: int):
    """Telegram'ning haqiqiy 🎲/🎯/🏀/⚽/🎳 animatsiyasini yuboradi va
    tushgan natijaga qarab +3 yoki −3 💎 beradi. Qiyin darajada ba'zi
    o'yinlarda bir necha marta tashlanadi va hammasi yutuq bo'lishi kerak."""
    cfg = DICE_GAMES[key]
    values, throws = cfg["tiers"][tier]

    head = f"{cfg['head']}\n\n📈 Daraja: {TIER_NAMES[tier]}\n{_dice_rules(key, tier)}"
    await safe_edit_message(
        query,
        f"{head}\n\n⏳ Tashlanmoqda...",
        reply_markup=None,
        parse_mode="HTML",
    )

    results = []
    for _ in range(throws):
        value = None
        try:
            msg = await context.bot.send_dice(
                chat_id=query.message.chat_id, emoji=cfg["emoji"]
            )
            value = msg.dice.value if msg and msg.dice else None
            await asyncio.sleep(DICE_WAIT_SECONDS)
        except TelegramError:
            # Animatsiyani yuborib bo'lmadi - natija baribir adolatli tarzda
            # tasodifiy tanlanadi (shu o'yinning haqiqiy qiymatlar oralig'ida).
            value = None
        if value is None:
            value = random.randint(1, cfg["max"])
        results.append(value)

    won = all(v in values for v in results)
    if throws == 1:
        template = cfg["win_text"] if won else cfg["lose_text"]
        header = template.format(v=results[0])
    else:
        nums = ", ".join(str(v) for v in results)
        header = f"{cfg['emoji']} Natijalar: <b>{nums}</b> — " + (
            "hammasi yutuq!" if won else "hammasi ham yetarli emas."
        )

    await (_win(query, header) if won else _lose(query, header))


# ---------------------------------------------------------------------------
# 🎮 Tanlov o'yinlarining natijasi
# ---------------------------------------------------------------------------

async def _handle_pick(query, context, key: str, chosen: int, tier: int):
    _text, options = _pick_config(key, tier)
    if not (0 <= chosen < len(options)):
        await query.answer("⚠️ Xatolik. Qaytadan urinib ko'ring.", show_alert=True)
        return
    await query.answer()

    # --- ✂️ Tosh-qaychi-qog'oz ---
    if key == "rps":
        bot_pick = random.randint(0, 2)
        header = f"Men: {_RPS_NAMES[bot_pick]}  |  Siz: {_RPS_NAMES[chosen]}"
        if bot_pick == chosen:
            if tier == 0:
                # 🤝 Oson darajada durrang - almaz o'zgarmaydi, o'yin qaytadan ochiladi.
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
            # 🟡/🔴 O'rtacha va qiyin darajada durrang = yutqazish (ogohlantirilgan).
            await _lose(query, header + "\n🤝 Durrang — bu darajada yutqazish hisoblanadi.")
            return
        # 0=tosh, 1=qaychi, 2=qog'oz -> foydalanuvchi yutadi:
        win = (chosen, bot_pick) in {(0, 1), (1, 2), (2, 0)}
        await (_win(query, header) if win else _lose(query, header))
        return

    # --- 🪙 Tanga (1, 2 yoki 3 ta tanga - hammasini topish kerak) ---
    if key == "coin":
        coins = PICK_TIER_PARAMS["coin"][tier]
        result = random.randrange(2 ** coins)
        header = (
            f"Tanga: {_coin_combo(result, coins)}  |  Siz: {_coin_combo(chosen, coins)}"
        )
        await (_win(query, header) if result == chosen else _lose(query, header))
        return

    # --- 🥤 Stakan ostidagi to'p ---
    if key == "cup":
        n = PICK_TIER_PARAMS["cup"][tier]
        result = random.randrange(n)
        header = f"To'p <b>{result + 1}-stakan</b> ostida edi. Siz {chosen + 1}-ni tanladingiz."
        await (_win(query, header) if result == chosen else _lose(query, header))
        return

    # --- 💣 Mina ---
    if key == "mine":
        cells, mine_count = PICK_TIER_PARAMS["mine"][tier]
        mines = set(random.sample(range(cells), mine_count))
        shown = ", ".join(str(m + 1) for m in sorted(mines))
        if chosen in mines:
            await _lose(query, f"💥 {chosen + 1}-katakda mina bor edi! (Minalar: {shown})")
        else:
            await _win(query, f"✔️ {chosen + 1}-katak xavfsiz! (Minalar: {shown})")
        return

    # --- 🔢 Raqamni top ---
    if key == "guessnum":
        n = PICK_TIER_PARAMS["guessnum"][tier]
        result = random.randrange(n)
        header = f"Men <b>{result + 1}</b> raqamini o'ylagandim. Siz {chosen + 1} dedingiz."
        await (_win(query, header) if result == chosen else _lose(query, header))
        return

    # --- 🎴 Katta yoki kichik (1..100 oraliqlarga bo'lingan) ---
    if key == "highlow":
        n = PICK_TIER_PARAMS["highlow"][tier]
        number = random.randint(1, 100)
        actual = next(i for i, (lo, hi) in enumerate(_highlow_buckets(n)) if lo <= number <= hi)
        header = f"Men o'ylagan son: <b>{number}</b>"
        await (_win(query, header) if actual == chosen else _lose(query, header))
        return

    # --- 🚦 Rangni top ---
    if key == "color":
        n = PICK_TIER_PARAMS["color"][tier]
        result = random.randrange(n)
        header = f"Men tanlagan rang: {_COLOR_POOL[result]}  |  Siz: {_COLOR_POOL[chosen]}"
        await (_win(query, header) if result == chosen else _lose(query, header))
        return

    await query.answer()


async def _handle_timeout(query, context, key: str):
    deducted = db.apply_hard_game_penalty(_user_id(query), PENALTY_AMOUNT)
    db.set_hard_game_cooldown(_user_id(query), _cd_key(key), TIMEOUT_COOLDOWN_HOURS)
    await safe_edit_message(
        query,
        TIMEOUT_TEXT + _penalty_suffix(deducted),
        reply_markup=_finish_keyboard(),
        parse_mode="HTML",
    )


async def _handle_answer(query, context, key: str, correct: int, chosen: int, ts: str,
                         limit: int = QUIZ_TIME_LIMIT):
    await query.answer()
    _cancel_warning_job(context, _user_id(query), ts)

    if _is_expired(ts, limit):
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
            tier = _safe_tier(parts[4]) if len(parts) > 4 else 0
            if key not in PICK_KEYS:
                await query.answer()
                return
            await _handle_pick(query, context, key, chosen, tier)
            return

        if action == "ans":
            key, correct, chosen, ts = parts[2], int(parts[3]), int(parts[4]), parts[5]
            limit = int(parts[6]) if len(parts) > 6 else QUIZ_TIME_LIMIT
            if limit not in QUIZ_TIME_BY_TIER:
                limit = QUIZ_TIME_LIMIT
            await _handle_answer(query, context, key, correct, chosen, ts, limit)
            return

        await query.answer()
    except (IndexError, ValueError):
        await query.answer("⚠️ Xatolik. Qaytadan urinib ko'ring.", show_alert=True)
