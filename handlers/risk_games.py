# -*- coding: utf-8 -*-
"""💣 PORTLOVCHI ALMAZ - tavakkal (omad) o'yinlari.

Joylashuvi:  💎 Almaz ishlash -> 🎮 O'yinlar -> (🟢 Oson | 🔥 Qiyin) tagida
             "💣 Portlovchi almaz" tugmasi.

Oqim:
  1. 💣 Portlovchi almaz  -> JIDDIY OGOHLANTIRISH + shartlar.
  2. "✅ Roziman"         -> 4 ta o'yin ro'yxati (rozilik bo'lmasa o'yinlar ko'rinmaydi).
  3. O'yin tanlanadi      -> raund ochiladi (almaz hali yechilmaydi), 2 ta tanlov.
  4. Tanlov bosiladi      -> natija darhol, ATOMAR hal qilinadi:
                             yutsa  +RG_STAKE 💎,  yutqazsa  −RG_STAKE 💎.

Halollik qoidalari (muhim):
  • Yutish ehtimoli FAQAT RG_WIN_PERCENT dan olinadi va ogohlantirish matnidagi
    foiz ham SHU o'zgaruvchidan chiqadi - matn bilan haqiqiy ehtimol hech
    qachon farq qilmaydi.
  • Natija serverda, kriptografik tasodifiylik (secrets) bilan aniqlanadi.
    Tugma ma'lumotida (callback_data) natija YO'Q - faqat raund raqami va tanlov.
  • Har bir raund bir marta hal bo'ladi (qayta bosish almazga ta'sir qilmaydi).
  • Balans stavkadan kam bo'lsa, o'yin boshlanmaydi va balans manfiy bo'lmaydi.

Callback prefiksi: "rg:..."
"""

import asyncio
import secrets

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from handlers.message_utils import safe_edit_message

import database as db

# ---------------------------------------------------------------------------
# Sozlamalar
# ---------------------------------------------------------------------------

RG_STAKE = 180            # Yutsa +180 💎, yutqazsa −180 💎
RG_WIN_PERCENT = 50       # Yutish ehtimoli (foizda). Ogohlantirish matni shundan olinadi.
RG_COOLDOWN_HOURS = 24    # Har bir o'yin uchun ALOHIDA kutish (soat)
RG_REVEAL_DELAY = 1.2     # Natija oldidan qisqa "hayajon" pauzasi (soniya)

_rng = secrets.SystemRandom()

# key -> (tugma nomi, savol matni, [1-tanlov, 2-tanlov])
RISK_GAMES = [
    (
        "bomb",
        "💎 Portlovchi almaz",
        "Ikkita almazdan BIRI portlaydi, ikkinchisi butun qoladi.\nQaysi almazni olasiz?",
        ["💎 Chap almaz", "💎 O'ng almaz"],
    ),
    (
        "coin",
        "🪙 Gerb yoki raqam",
        "Tanga tashlanadi.\nQaysi tomon tushadi?",
        ["🪙 Gerb", "🪙 Raqam"],
    ),
    (
        "card",
        "🃏 Qizil yoki qora",
        "Aralashtirilgan dastadan bitta karta olinadi.\nUning rangi qanday?",
        ["♥️ Qizil", "♠️ Qora"],
    ),
    (
        "dice",
        "🎲 Juft yoki toq",
        "Zar tashlanadi.\nChiqqan son juft bo'ladimi yoki toq?",
        ["2️⃣ Juft", "1️⃣ Toq"],
    ),
]
RISK_TITLES = {k: t for k, t, _, _ in RISK_GAMES}
RISK_PROMPTS = {k: p for k, _, p, _ in RISK_GAMES}
RISK_CHOICES = {k: c for k, _, _, c in RISK_GAMES}


def _cooldown_key(game_key: str) -> str:
    # hg:/eg: o'yinlari kalitlari bilan to'qnashmasligi uchun prefiks.
    return f"rg_{game_key}"


def _fmt_time(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0:
        return f"{h} soat {m} daqiqa"
    return f"{m} daqiqa"


def _roll_win() -> bool:
    """Yutdimi? Ehtimol = RG_WIN_PERCENT / 100 (kriptografik tasodifiylik)."""
    return _rng.randrange(100) < RG_WIN_PERCENT


# ---------------------------------------------------------------------------
# Matnlar
# ---------------------------------------------------------------------------

def _warning_text() -> str:
    lose_percent = 100 - RG_WIN_PERCENT
    return (
        "🚨⚠️ <b>JIDDIY OGOHLANTIRISH</b> ⚠️🚨\n\n"
        "💣 <b>PORTLOVCHI ALMAZ</b> — bu <b>TAVAKKAL (omad) o'yini</b>. "
        "Natija 100% tasodifga bog'liq: bilim ham, tajriba ham, hiyla ham "
        "yordam bermaydi.\n\n"
        "📜 <b>SHARTLAR:</b>\n"
        f"1️⃣ Har bir o'yinda: yutsangiz <b>+{RG_STAKE} 💎</b>, "
        f"yutqazsangiz <b>−{RG_STAKE} 💎</b>.\n"
        f"2️⃣ Yutish ehtimoli: <b>{RG_WIN_PERCENT}%</b>, "
        f"yutqazish ehtimoli: <b>{lose_percent}%</b>.\n"
        f"3️⃣ Yutqazgan {RG_STAKE} 💎 <b>QAYTARILMAYDI</b> — na bot, na admin "
        "qaytarib bera olmaydi.\n"
        f"4️⃣ O'ynash uchun hisobingizda kamida <b>{RG_STAKE} 💎</b> bo'lishi kerak.\n"
        f"5️⃣ Har bir o'yin {RG_COOLDOWN_HOURS} soatda 1 marta o'ynaladi.\n"
        "6️⃣ Tugmani bosgan zahoti natija hal bo'ladi — orqaga yo'l yo'q.\n"
        "7️⃣ Faqat yo'qotsangiz ham afsuslanmaydigan almaz bilan o'ynang.\n"
        "8️⃣ Bu bo'lim faqat <b>18 yoshdan oshganlar</b> uchun.\n\n"
        "🛑 Biz sizni <b>MAJBURLAMAYMIZ</b>. Rozi bo'lmasangiz — pastdagi "
        "«Orqaga» tugmasini bosing.\n\n"
        "Shartlarni o'qib, to'liq roziligingizni bildirsangiz — davom eting 👇"
    )


def _list_text(balance: int) -> str:
    return (
        "💣 <b>PORTLOVCHI ALMAZ</b>\n\n"
        f"💎 Hisobingiz: <b>{balance}</b>\n"
        f"🎯 Har bir o'yin: <b>±{RG_STAKE} 💎</b> ({RG_WIN_PERCENT}% / {100 - RG_WIN_PERCENT}%)\n"
        f"⏳ Har bir o'yin {RG_COOLDOWN_HOURS} soatda 1 marta.\n\n"
        "O'yinni tanlang 👇"
    )


def _game_text(game_key: str) -> str:
    return (
        f"{RISK_TITLES[game_key]}\n\n"
        f"{RISK_PROMPTS[game_key]}\n\n"
        f"⚠️ Tanlovni bosgan zahoti hisobingizdan <b>±{RG_STAKE} 💎</b> hal bo'ladi.\n"
        f"🎯 Yutish: {RG_WIN_PERCENT}%  |  💥 Yutqazish: {100 - RG_WIN_PERCENT}%"
    )


# ---------------------------------------------------------------------------
# Klaviaturalar
# ---------------------------------------------------------------------------

def _warning_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Shartlarni o'qidim, 18+ man va roziman", callback_data="rg:agree")],
            [InlineKeyboardButton("⬅️ Orqaga (o'ynamayman)", callback_data="hg:intro")],
        ]
    )


def _list_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(title, callback_data=f"rg:play:{key}")]
        for key, title, _, _ in RISK_GAMES
    ]
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="hg:intro")])
    return InlineKeyboardMarkup(rows)


def _game_keyboard(round_id: int, game_key: str) -> InlineKeyboardMarkup:
    a, b = RISK_CHOICES[game_key]
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(a, callback_data=f"rg:pick:{round_id}:0"),
                InlineKeyboardButton(b, callback_data=f"rg:pick:{round_id}:1"),
            ],
            [InlineKeyboardButton("❌ Bekor qilish (almaz yechilmaydi)", callback_data=f"rg:cancel:{round_id}")],
        ]
    )


def _after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            # Qayta o'ynash uchun shartlar YANA ko'rsatiladi (har safar rozilik).
            [InlineKeyboardButton("💣 Qayta o'ynash (shartlar bilan)", callback_data="rg:intro")],
            [InlineKeyboardButton("⬅️ O'yinlar menyusi", callback_data="hg:intro")],
        ]
    )


# ---------------------------------------------------------------------------
# Natijani ko'rsatish (qaysi tomon / qaysi karta / qaysi son chiqqani)
# ---------------------------------------------------------------------------

def _result_line(game_key: str, choice: int, won: bool) -> str:
    """Yutdi/yutqazdi allaqachon hal bo'lgan; shunga MOS keladigan sahnani
    chiroyli ko'rsatadi (natija shu yerda o'zgartirilmaydi)."""
    if game_key == "bomb":
        exploded = (1 - choice) if won else choice
        names = ["chap", "o'ng"]
        return f"💥 Portlagan almaz: <b>{names[exploded]}</b> almaz edi."

    if game_key == "coin":
        landed = choice if won else 1 - choice
        return f"🪙 Tanga tushdi: <b>{'Gerb' if landed == 0 else 'Raqam'}</b>."

    if game_key == "card":
        landed = choice if won else 1 - choice  # 0 - qizil, 1 - qora
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        suits = ["♥️", "♦️"] if landed == 0 else ["♠️", "♣️"]
        card = f"{_rng.choice(suits)} {_rng.choice(ranks)}"
        return f"🃏 Karta: <b>{card}</b> ({'qizil' if landed == 0 else 'qora'})."

    if game_key == "dice":
        landed = choice if won else 1 - choice  # 0 - juft, 1 - toq
        value = _rng.choice([2, 4, 6] if landed == 0 else [1, 3, 5])
        faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        return f"🎲 Zar: {faces[value - 1]} <b>{value}</b> ({'juft' if landed == 0 else 'toq'})."

    return ""


# ---------------------------------------------------------------------------
# Handlerlar
# ---------------------------------------------------------------------------

async def _show_warning(query):
    await safe_edit_message(
        query, _warning_text(), reply_markup=_warning_keyboard(), parse_mode="HTML"
    )


async def _show_list(query):
    balance = db.get_quiz_diamonds(query.from_user.id)
    await safe_edit_message(
        query, _list_text(balance), reply_markup=_list_keyboard(), parse_mode="HTML"
    )


async def _open_round(query, game_key: str):
    user_id = query.from_user.id

    if game_key not in RISK_TITLES:
        await query.answer()
        return

    balance = db.get_quiz_diamonds(user_id)
    if balance < RG_STAKE:
        await query.answer(
            f"💎 Yetarli almaz yo'q.\nO'ynash uchun kamida {RG_STAKE} 💎 kerak, "
            f"sizda {balance} 💎 bor.",
            show_alert=True,
        )
        return

    allowed, remaining = db.check_hard_game_cooldown(user_id, _cooldown_key(game_key))
    if not allowed:
        await query.answer(
            f"⏳ Bu o'yinni {_fmt_time(remaining)}dan keyin qayta o'ynashingiz mumkin.",
            show_alert=True,
        )
        return

    await query.answer()
    round_id = db.risk_create_round(user_id, game_key, RG_STAKE)
    await safe_edit_message(
        query,
        _game_text(game_key),
        reply_markup=_game_keyboard(round_id, game_key),
        parse_mode="HTML",
    )


async def _pick(query, round_id: int, choice: int):
    user_id = query.from_user.id
    if choice not in (0, 1):
        await query.answer()
        return

    rnd = db.risk_get_round(round_id, user_id)
    if not rnd:
        await query.answer("⚠️ Raund topilmadi. Qaytadan boshlang.", show_alert=True)
        return
    game_key = rnd["game_key"]

    # Natija shu yerda, serverda aniqlanadi va raund ATOMAR yopiladi.
    won = _roll_win()
    res = db.risk_settle_round(round_id, user_id, choice, won)
    status = res["status"]

    if status == "closed":
        await query.answer("Bu raund allaqachon yakunlangan.", show_alert=True)
        return
    if status == "expired":
        await query.answer()
        await safe_edit_message(
            query,
            "⏱ <b>Vaqt tugadi.</b>\nHech qanday almaz yechilmadi. Xohlasangiz, qaytadan boshlang.",
            reply_markup=_after_keyboard(),
            parse_mode="HTML",
        )
        return
    if status == "insufficient":
        await query.answer()
        await safe_edit_message(
            query,
            f"💎 Hisobingizda yetarli almaz yo'q (kerak: {RG_STAKE} 💎).\n"
            "Hech narsa yechilmadi.",
            reply_markup=_after_keyboard(),
            parse_mode="HTML",
        )
        return
    if status == "missing":
        await query.answer("⚠️ Raund topilmadi.", show_alert=True)
        return

    await query.answer()

    # Shu o'yin uchun kutish faqat haqiqiy natija chiqqanda qo'yiladi.
    db.set_hard_game_cooldown(user_id, _cooldown_key(game_key), RG_COOLDOWN_HOURS)

    # Qisqa hayajon pauzasi (natija allaqachon hal bo'lgan).
    await safe_edit_message(
        query,
        f"{RISK_TITLES[game_key]}\n\n⏳ <b>Natija aniqlanmoqda...</b>",
        parse_mode="HTML",
    )
    await asyncio.sleep(RG_REVEAL_DELAY)

    scene = _result_line(game_key, choice, res["status"] == "won")
    balance = res["balance"]
    if res["status"] == "won":
        text = (
            f"{RISK_TITLES[game_key]}\n\n{scene}\n\n"
            f"🎉 <b>YUTDINGIZ!</b>\n💎 <b>+{RG_STAKE}</b> almaz qo'shildi.\n"
            f"💎 Hisobingiz: <b>{balance}</b>"
        )
    else:
        text = (
            f"{RISK_TITLES[game_key]}\n\n{scene}\n\n"
            f"💥 <b>YUTQAZDINGIZ.</b>\n💎 <b>−{RG_STAKE}</b> almaz yechildi.\n"
            f"💎 Hisobingiz: <b>{balance}</b>"
        )
    text += f"\n\n⏳ Bu o'yin uchun {RG_COOLDOWN_HOURS} soat kuting."
    await safe_edit_message(query, text, reply_markup=_after_keyboard(), parse_mode="HTML")


async def _cancel(query, round_id: int):
    db.risk_cancel_round(round_id, query.from_user.id)
    await query.answer("Bekor qilindi. Almaz yechilmadi.")
    await _show_list(query)


async def on_risk_games_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha "rg:..." callbacklarini boshqaradi."""
    query = update.callback_query
    parts = query.data.split(":")

    try:
        action = parts[1]

        if action == "intro":
            await query.answer()
            await _show_warning(query)
            return

        if action == "agree":
            await query.answer()
            await _show_list(query)
            return

        if action == "play":
            await _open_round(query, parts[2])
            return

        if action == "pick":
            await _pick(query, int(parts[2]), int(parts[3]))
            return

        if action == "cancel":
            await _cancel(query, int(parts[2]))
            return

        await query.answer()
    except (IndexError, ValueError):
        await query.answer("⚠️ Xatolik. Qaytadan urinib ko'ring.", show_alert=True)
