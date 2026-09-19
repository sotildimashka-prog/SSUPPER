# -*- coding: utf-8 -*-
"""💣 PORTLOVCHI ALMAZ - tavakkal (omad) o'yinlari.

Joylashuvi:  💎 Almaz ishlash -> 🎮 O'yinlar -> (🟢 Oson | 🔥 Qiyin) tagida
             "💣 Portlovchi almaz" tugmasi.

Har bir o'yinda RG_CELLS (70) ta yopiq katak bor. FAQAT BITTASI g'olib katak,
qolgan 69 tasi "portlaydi". Yutish ehtimoli = 1 / RG_CELLS (~1.4%).

Oqim:
  1. 💣 Portlovchi almaz  -> JIDDIY OGOHLANTIRISH + shartlar (ehtimol ham shu yerda).
  2. "✅ Roziman"         -> 4 ta o'yin ro'yxati (rozilik bo'lmasa o'yinlar ko'rinmaydi).
  3. O'yin tanlanadi      -> raund ochiladi (almaz hali yechilmaydi), 70 ta katak.
  4. Katak bosiladi       -> natija darhol, ATOMAR hal qilinadi:
                             yutsa  +RG_PRIZE 💎,  yutqazsa  −RG_STAKE 💎.

Halollik qoidalari (muhim):
  • Ogohlantirishdagi ehtimol RG_CELLS dan hisoblanadi - matn bilan haqiqiy
    ehtimol hech qachon farq qilmaydi.
  • G'olib katak serverda, kriptografik tasodifiylik (secrets) bilan, katak
    bosilgan paytda aniqlanadi. Tugma ma'lumotida (callback_data) natija YO'Q.
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

RG_CELLS = 70             # Har bir o'yindagi kataklar soni (FAQAT bittasi yutadi)
RG_COLUMNS = 7            # Katakchalar bir qatorda nechta (70 = 7 x 10)
RG_STAKE = 180            # Yutqazsa −180 💎
RG_PRIZE = 180            # Yutsa +180 💎  (istasangiz shu yerdan oshiring)
RG_COOLDOWN_HOURS = 24    # Har bir o'yin uchun ALOHIDA kutish (soat)
RG_REVEAL_DELAY = 1.2     # Natija oldidan qisqa "hayajon" pauzasi (soniya)

_rng = secrets.SystemRandom()

# key -> (nomi, tugma belgisi, savol matni)
RISK_GAMES = [
    (
        "bomb",
        "💎 Portlovchi almaz",
        "💎",
        f"{RG_CELLS} ta almaz turibdi. Ulardan FAQAT BITTASI butun — "
        f"qolgan {RG_CELLS - 1} tasi portlaydi!\nO'z almazingizni tanlang:",
    ),
    (
        "door",
        "🚪 Sirli eshiklar",
        "🚪",
        f"{RG_CELLS} ta eshik. Faqat bittasining ortida sovrin bor, "
        f"qolgan {RG_CELLS - 1} tasi tuzoq!\nQaysi eshikni ochasiz?",
    ),
    (
        "card",
        "🃏 Omadli karta",
        "🃏",
        f"{RG_CELLS} ta yopiq karta. Faqat bittasi omadli karta, "
        f"qolgan {RG_CELLS - 1} tasi bo'sh!\nBirini tanlang:",
    ),
    (
        "chest",
        "📦 Sirli sandiqlar",
        "📦",
        f"{RG_CELLS} ta sandiq. Faqat bittasining ichida xazina bor, "
        f"qolgan {RG_CELLS - 1} tasi portlaydi!\nQaysi sandiqni ochasiz?",
    ),
]
RISK_TITLES = {k: t for k, t, _, _ in RISK_GAMES}
RISK_ICONS = {k: i for k, _, i, _ in RISK_GAMES}
RISK_PROMPTS = {k: p for k, _, _, p in RISK_GAMES}


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


def _win_percent_text() -> str:
    """Yutish ehtimoli matni (RG_CELLS dan hisoblanadi)."""
    return f"{100 / RG_CELLS:.1f}%".replace(".", ",")


def _lose_percent_text() -> str:
    return f"{100 - 100 / RG_CELLS:.1f}%".replace(".", ",")


def _draw_winning_cell() -> int:
    """G'olib katak (0..RG_CELLS-1) - kriptografik tasodifiylik."""
    return _rng.randrange(RG_CELLS)


# ---------------------------------------------------------------------------
# Matnlar
# ---------------------------------------------------------------------------

def _warning_text() -> str:
    return (
        "🚨⚠️ <b>JIDDIY OGOHLANTIRISH</b> ⚠️🚨\n\n"
        "💣 <b>PORTLOVCHI ALMAZ</b> — bu <b>TAVAKKAL (omad) o'yini</b> va "
        "<b>juda qiyin</b>. Natija 100% tasodifga bog'liq: bilim ham, tajriba "
        "ham, hiyla ham yordam bermaydi.\n\n"
        f"🎯 <b>YUTISH EHTIMOLI: {RG_CELLS} tadan 1 ta ({_win_percent_text()})</b>\n"
        f"💥 Yutqazish ehtimoli: {_lose_percent_text()}\n"
        f"Ya'ni har {RG_CELLS} urinishdan o'rtacha faqat 1 tasida yutasiz.\n\n"
        "📜 <b>SHARTLAR:</b>\n"
        f"1️⃣ Har bir o'yinda {RG_CELLS} ta katak bor, FAQAT bittasi yutuq.\n"
        f"2️⃣ Yutsangiz <b>+{RG_PRIZE} 💎</b>, yutqazsangiz <b>−{RG_STAKE} 💎</b>.\n"
        f"3️⃣ Yutqazgan {RG_STAKE} 💎 <b>QAYTARILMAYDI</b> — na bot, na admin "
        "qaytarib bera olmaydi.\n"
        f"4️⃣ O'ynash uchun hisobingizda kamida <b>{RG_STAKE} 💎</b> bo'lishi kerak.\n"
        f"5️⃣ Har bir o'yin {RG_COOLDOWN_HOURS} soatda 1 marta o'ynaladi.\n"
        "6️⃣ Katakni bosgan zahoti natija hal bo'ladi — orqaga yo'l yo'q.\n"
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
        f"🎯 Yutish: <b>{RG_CELLS} tadan 1</b> ({_win_percent_text()}) → <b>+{RG_PRIZE} 💎</b>\n"
        f"💥 Yutqazish: <b>−{RG_STAKE} 💎</b>\n"
        f"⏳ Har bir o'yin {RG_COOLDOWN_HOURS} soatda 1 marta.\n\n"
        "O'yinni tanlang 👇"
    )


def _game_text(game_key: str) -> str:
    return (
        f"<b>{RISK_TITLES[game_key]}</b>\n\n"
        f"{RISK_PROMPTS[game_key]}\n\n"
        f"🎯 Yutish: {RG_CELLS} tadan 1 ({_win_percent_text()})  →  <b>+{RG_PRIZE} 💎</b>\n"
        f"💥 Yutqazish: <b>−{RG_STAKE} 💎</b>\n"
        "⚠️ Katakni bosgan zahoti natija hal bo'ladi!"
    )


def _board_text(game_key: str, chosen: int, winner: int) -> str:
    """Natijadan keyingi maydon: 🏆 - g'olib katak, 💥 - siz tanlagan (xato)
    katak, ▫️ - qolganlari. Kataklar tugmalardagi joylashuv bilan bir xil."""
    lines = []
    for r in range(0, RG_CELLS, RG_COLUMNS):
        row = []
        for idx in range(r, min(r + RG_COLUMNS, RG_CELLS)):
            if idx == winner:
                row.append("🏆")
            elif idx == chosen:
                row.append("💥")
            else:
                row.append("▫️")
        lines.append("".join(row))
    return "\n".join(lines)


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
    """RG_CELLS ta katak - chiroyli to'r (RG_COLUMNS ustun) + bekor qilish."""
    icon = RISK_ICONS[game_key]
    rows, row = [], []
    for idx in range(RG_CELLS):
        row.append(InlineKeyboardButton(icon, callback_data=f"rg:pick:{round_id}:{idx}"))
        if len(row) == RG_COLUMNS:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("❌ Bekor qilish (almaz yechilmaydi)", callback_data=f"rg:cancel:{round_id}")])
    return InlineKeyboardMarkup(rows)


def _after_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            # Qayta o'ynash uchun shartlar YANA ko'rsatiladi (har safar rozilik).
            [InlineKeyboardButton("💣 Qayta o'ynash (shartlar bilan)", callback_data="rg:intro")],
            [InlineKeyboardButton("⬅️ O'yinlar menyusi", callback_data="hg:intro")],
        ]
    )


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
    if not (0 <= choice < RG_CELLS):
        await query.answer()
        return

    rnd = db.risk_get_round(round_id, user_id)
    if not rnd:
        await query.answer("⚠️ Raund topilmadi. Qaytadan boshlang.", show_alert=True)
        return
    game_key = rnd["game_key"]
    if game_key not in RISK_TITLES:
        await query.answer()
        return

    # G'olib katak shu yerda, serverda aniqlanadi va raund ATOMAR yopiladi.
    winner = _draw_winning_cell()
    won = choice == winner
    res = db.risk_settle_round(round_id, user_id, choice, won, prize=RG_PRIZE)
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
        f"<b>{RISK_TITLES[game_key]}</b>\n\n⏳ <b>Natija aniqlanmoqda...</b>",
        parse_mode="HTML",
    )
    await asyncio.sleep(RG_REVEAL_DELAY)

    board = _board_text(game_key, choice, winner)
    balance = res["balance"]
    if won:
        text = (
            f"<b>{RISK_TITLES[game_key]}</b>\n\n{board}\n\n"
            f"🏆 <b>YUTDINGIZ!</b> Siz {RG_CELLS} tadan 1 ta g'olib katakni topdingiz!\n"
            f"💎 <b>+{res['prize']}</b> almaz qo'shildi.\n"
            f"💎 Hisobingiz: <b>{balance}</b>"
        )
    else:
        text = (
            f"<b>{RISK_TITLES[game_key]}</b>\n\n{board}\n\n"
            "💥 <b>YUTQAZDINGIZ.</b> Siz tanlagan katak portladi.\n"
            f"🏆 — g'olib katak, 💥 — sizning tanlovingiz.\n"
            f"💎 <b>−{res['stake']}</b> almaz yechildi.\n"
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
