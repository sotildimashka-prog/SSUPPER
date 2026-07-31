# -*- coding: utf-8 -*-
"""🎮 Mini O'yinlar bo'limi.

Ikki rejim mavjud:
  - free (🎮 Oddiy O'yinlar)      -> mukofotsiz, cheksiz o'ynash mumkin
  - paid (🏆 Mukofotli O'yinlar)  -> g'alabada 10 💎 Almaz, har bir o'yin
                                      foydalanuvchi uchun 24 soatda 1 marta
"""

import random
import asyncio
import time

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

import database as db
from keyboards import BTN_MINI_GAMES  # noqa: F401 (bot.py orqali chaqiriladi)

REWARD_AMOUNT = 10

GAMES = [
    ("mine", "💣 Minani top"),
    ("target", "🎯 Nishonni ur"),
    ("dice", "🎲 Kubik tashlash"),
    ("coin", "🪙 Tanga tashlash"),
    ("card", "🃏 Kartani tanla"),
    ("slot", "🎰 Slot mashina"),
    ("number", "🔢 Sonni top"),
    ("quiz", "❓ FF Viktorina"),
    ("reflex", "⚡ Refleks testi"),
    ("chicken", "🐔 Tovuqmi yoki tuxummi"),
]
GAME_TITLES = dict(GAMES)

WIN_TEXT = "🎉 Tabriklaymiz!\nSiz {amount} 💎 Almaz yutdingiz!"
WIN_TEXT_FREE = "✅ Siz yutdingiz! 🎉"
LOSE_TEXT = "😔 Bu safar omad kelmadi.\nYana urinib ko'ring!"


def _fmt_time(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0:
        return f"{h} soat {m} daqiqa"
    return f"{m} daqiqa"


def _mode_title(mode: str) -> str:
    return "🏆 Mukofotli O'yinlar" if mode == "paid" else "🎮 Oddiy O'yinlar"


def _result_keyboard(mode: str, game_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔁 Qayta o'ynash", callback_data=f"games:open:{mode}:{game_key}")],
            [InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data=f"games:list:{mode}")],
        ]
    )


def _back_keyboard(mode: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ O'yinlar ro'yxati", callback_data=f"games:list:{mode}")]]
    )


# ---------------------------------------------------------------------------
# Kirish nuqtalari
# ---------------------------------------------------------------------------

async def on_games_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎮 Mini O'yinlar (Reply tugma)."""
    text = (
        "🎮 <b>Mini O'yinlar</b>\n\n"
        "Qaysi rejimda o'ynamoqchisiz?\n\n"
        "🎮 <b>Oddiy O'yinlar</b> 🎲\n"
        "Hech qanday mukofot berilmaydi. Faqat qiziqarli mini o'yinlarni "
        "o'ynab vaqtni maroqli o'tkazing!\n\n"
        "🏆 <b>Mukofotli O'yinlar</b> 🎁\n"
        "G'olib bo'lsangiz har bir o'yinda 10 💎 Almaz mukofotiga ega bo'lasiz!"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎮 Oddiy O'yinlar 🎲", callback_data="games:mode:free")],
            [InlineKeyboardButton("🏆 Mukofotli O'yinlar 🎁", callback_data="games:mode:paid")],
        ]
    )
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


async def _show_mode_select(query):
    text = (
        "🎮 <b>Mini O'yinlar</b>\n\n"
        "Qaysi rejimda o'ynamoqchisiz?\n\n"
        "🎮 <b>Oddiy O'yinlar</b> 🎲\n"
        "Hech qanday mukofot berilmaydi. Faqat qiziqarli mini o'yinlarni "
        "o'ynab vaqtni maroqli o'tkazing!\n\n"
        "🏆 <b>Mukofotli O'yinlar</b> 🎁\n"
        "G'olib bo'lsangiz har bir o'yinda 10 💎 Almaz mukofotiga ega bo'lasiz!"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎮 Oddiy O'yinlar 🎲", callback_data="games:mode:free")],
            [InlineKeyboardButton("🏆 Mukofotli O'yinlar 🎁", callback_data="games:mode:paid")],
        ]
    )
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")


async def _show_game_list(query, mode: str):
    rows = []
    row = []
    for key, title in GAMES:
        row.append(InlineKeyboardButton(title, callback_data=f"games:open:{mode}:{key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="games:back")])

    if mode == "paid":
        text = "🏆 <b>Mukofotli O'yinlar</b> 🎁\n\nG'olib bo'lsangiz har biridan +10 💎 Almaz!\nHar bir o'yin 24 soatda 1 marta o'ynaladi.\n\nO'yinni tanlang:"
    else:
        text = "🎮 <b>Oddiy O'yinlar</b> 🎲\n\nMukofotsiz, xohlagancha o'ynang!\n\nO'yinni tanlang:"

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="HTML")


async def on_games_root_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mini o'yinlarga oid barcha callbacklar shu yerdan tarqatiladi:
    - "games:..."           -> menyu navigatsiyasi (mode/list/open/back)
    - "<game_key>:<mode>:.." -> o'yin ichidagi harakat (natija)."""
    query = update.callback_query
    data = query.data
    parts = data.split(":")

    try:
        if parts[0] == "games":
            if data == "games:back":
                await query.answer()
                await _show_mode_select(query)
                return

            if parts[1] in ("mode", "list"):
                mode = parts[2]
                await query.answer()
                await _show_game_list(query, mode)
                return

            if parts[1] == "open":
                mode, key = parts[2], parts[3]
                await _open_game(query, context, mode, key)
                return

            await query.answer()
            return

        # O'yin ichidagi harakat: "<key>:<mode>:..." (masalan "mine:paid:3:5")
        key = parts[0]
        mode = parts[1]
        rest = parts[2:]

        handler = _ACTION_HANDLERS.get(key)
        if handler:
            await handler(query, context, mode, rest)
        else:
            await query.answer()
    except (IndexError, ValueError):
        await query.answer("⚠️ Xatolik. Qaytadan urinib ko'ring.", show_alert=True)


def _user_id(query) -> int:
    return query.from_user.id


async def _check_and_consume_cooldown(query, mode: str, key: str) -> bool:
    """Mukofotli rejimda cooldownni tekshiradi. Bo'sh bo'lsa, band qilib qo'yadi."""
    if mode != "paid":
        return True
    user_id = _user_id(query)
    allowed, remaining = db.check_game_cooldown(user_id, key)
    if not allowed:
        title = GAME_TITLES.get(key, "Bu o'yin")
        await query.answer(
            f"⏳ {title} allaqachon bugun o'ynalgan.\nYana {_fmt_time(remaining)}dan keyin urinib ko'ring.",
            show_alert=True,
        )
        return False
    db.set_game_cooldown(user_id, key)
    await query.answer()
    return True


async def _finish(query, context, mode, key, won: bool):
    if won:
        if mode == "paid":
            db.give_game_reward(_user_id(query), REWARD_AMOUNT)
            text = "🎉 <b>Tabriklaymiz!</b>\nSiz 10 💎 Almaz yutdingiz!"
        else:
            text = "✅ <b>Siz yutdingiz!</b> 🎉"
    else:
        text = "😔 <b>Bu safar omad kelmadi.</b>\nYana urinib ko'ring!"
    await query.edit_message_text(text, reply_markup=_result_keyboard(mode, key), parse_mode="HTML")


# ---------------------------------------------------------------------------
# O'yinlarni ochish (birinchi ekran)
# ---------------------------------------------------------------------------

async def _open_game(query, context, mode, key):
    if key == "mine":
        if not await _check_and_consume_cooldown(query, mode, key):
            return
        mine_idx = random.randint(0, 8)
        rows = []
        for r in range(3):
            row = []
            for c in range(3):
                idx = r * 3 + c
                row.append(InlineKeyboardButton("⬜", callback_data=f"mine:{mode}:{mine_idx}:{idx}"))
            rows.append(row)
        rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data=f"games:list:{mode}")])
        await query.edit_message_text(
            "💣 <b>Minani top!</b>\n\n9 ta katakdan 8 tasi xavfsiz, 1 tasi mina.\nBitta katakni tanlang:",
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="HTML",
        )
        return

    if key == "target":
        if not await _check_and_consume_cooldown(query, mode, key):
            return
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🎯 Otish", callback_data=f"target:{mode}:shoot")],
                [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"games:list:{mode}")],
            ]
        )
        await query.edit_message_text(
            "🎯 <b>Nishonni ur!</b>\n\n80-100 ball headshot hisoblanadi. Omad!",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    if key == "dice":
        if not await _check_and_consume_cooldown(query, mode, key):
            return
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🎲 Tashlash", callback_data=f"dice:{mode}:roll")],
                [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"games:list:{mode}")],
            ]
        )
        await query.edit_message_text(
            "🎲 <b>Kubik tashlash</b>\n\n6 (olti) tushsa - yutasiz!",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    if key == "coin":
        if not await _check_and_consume_cooldown(query, mode, key):
            return
        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🪙 Gerb", callback_data=f"coin:{mode}:gerb"),
                    InlineKeyboardButton("🪙 Raqam", callback_data=f"coin:{mode}:raqam"),
                ],
                [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"games:list:{mode}")],
            ]
        )
        await query.edit_message_text(
            "🪙 <b>Tanga tashlash</b>\n\nGerb yoki Raqamni tanlang:",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    if key == "card":
        if not await _check_and_consume_cooldown(query, mode, key):
            return
        prize_idx = random.randint(0, 2)
        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🃏 1", callback_data=f"card:{mode}:{prize_idx}:0"),
                    InlineKeyboardButton("🃏 2", callback_data=f"card:{mode}:{prize_idx}:1"),
                    InlineKeyboardButton("🃏 3", callback_data=f"card:{mode}:{prize_idx}:2"),
                ],
                [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"games:list:{mode}")],
            ]
        )
        await query.edit_message_text(
            "🃏 <b>Kartani tanla</b>\n\n3 ta kartadan faqat bittasida sovrin bor:",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    if key == "slot":
        if not await _check_and_consume_cooldown(query, mode, key):
            return
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🎰 Aylantirish", callback_data=f"slot:{mode}:spin")],
                [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"games:list:{mode}")],
            ]
        )
        await query.edit_message_text(
            "🎰 <b>Slot mashina</b>\n\n3 ta emoji bir xil chiqsa - yutasiz!",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    if key == "number":
        if not await _check_and_consume_cooldown(query, mode, key):
            return
        target = random.randint(1, 100)
        db.start_number_game(_user_id(query), target, 5, mode)
        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Bekor qilish", callback_data=f"number:{mode}:cancel")]]
        )
        await query.edit_message_text(
            "🔢 <b>Sonni top!</b>\n\nMen 1 dan 100 gacha son o'yladim.\n"
            "5 ta taxmin huquqingiz bor. Raqamni yozib yuboring 👇",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    if key == "quiz":
        if not await _check_and_consume_cooldown(query, mode, key):
            return
        from data.quiz_data import QUESTIONS

        q = random.choice(QUESTIONS)
        options = q["options"]
        correct = q["correct"]
        rows = [
            [InlineKeyboardButton(opt, callback_data=f"quiz:{mode}:{correct}:{i}")]
            for i, opt in enumerate(options)
        ]
        rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data=f"games:list:{mode}")])
        await query.edit_message_text(
            f"❓ <b>Free Fire Viktorinasi</b>\n\n{q['question']}",
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="HTML",
        )
        return

    if key == "reflex":
        if not await _check_and_consume_cooldown(query, mode, key):
            return
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✅ Tayyorman", callback_data=f"reflex:{mode}:ready")],
                [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"games:list:{mode}")],
            ]
        )
        await query.edit_message_text(
            "⚡ <b>Refleks testi</b>\n\n\"Tayyorman\" tugmasini bosing, so'ng "
            "tasodifiy vaqtda \"🔴 BOS!\" tugmasi chiqadi. 1 soniyadan tez bosing!",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    if key == "chicken":
        if not await _check_and_consume_cooldown(query, mode, key):
            return
        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🐔", callback_data=f"chicken:{mode}:tovuq"),
                    InlineKeyboardButton("🥚", callback_data=f"chicken:{mode}:tuxum"),
                ],
                [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"games:list:{mode}")],
            ]
        )
        await query.edit_message_text(
            "🐔 <b>Tovuqmi yoki tuxummi?</b> 🥚\n\nBirini tanlang, omad tilaymiz!",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    await query.answer()


# ---------------------------------------------------------------------------
# O'yin harakatlari (natija chiqarish)
# ---------------------------------------------------------------------------

async def _act_mine(query, context, mode, rest):
    mine_idx, cell_idx = int(rest[0]), int(rest[1])
    await query.answer()
    won = cell_idx != mine_idx
    if not won:
        await query.edit_message_text(
            "💥 <b>Mina portladi!</b>\nMukofot yo'q.",
            reply_markup=_result_keyboard(mode, "mine"),
            parse_mode="HTML",
        )
        return
    await _finish(query, context, mode, "mine", True)


async def _act_target(query, context, mode, rest):
    await query.answer()
    score = random.randint(0, 100)
    won = score >= 80
    prefix = f"🎯 Natija: {score} ball\n\n"
    if won:
        await _finish_with_prefix(query, mode, "target", True, prefix + "🎯 Headshot!\n")
    else:
        await query.edit_message_text(
            prefix + "❌ Nishonga tegmadi.",
            reply_markup=_result_keyboard(mode, "target"),
            parse_mode="HTML",
        )


async def _act_dice(query, context, mode, rest):
    await query.answer()
    value = random.randint(1, 6)
    won = value == 6
    dice_faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    prefix = f"{dice_faces[value - 1]} Chiqdi: {value}\n\n"
    if won:
        await _finish_with_prefix(query, mode, "dice", True, prefix)
    else:
        await query.edit_message_text(
            prefix + "😔 Omad kelmadi.",
            reply_markup=_result_keyboard(mode, "dice"),
            parse_mode="HTML",
        )


async def _act_coin(query, context, mode, rest):
    choice = rest[0]
    await query.answer()
    result = random.choice(["gerb", "raqam"])
    won = choice == result
    result_label = "🪙 Gerb" if result == "gerb" else "🪙 Raqam"
    prefix = f"Natija: {result_label}\n\n"
    if won:
        await _finish_with_prefix(query, mode, "coin", True, prefix)
    else:
        await query.edit_message_text(
            prefix + "😔 Bu safar omad kelmadi.\nYana urinib ko'ring!",
            reply_markup=_result_keyboard(mode, "coin"),
            parse_mode="HTML",
        )


async def _act_card(query, context, mode, rest):
    prize_idx, chosen_idx = int(rest[0]), int(rest[1])
    await query.answer()
    won = chosen_idx == prize_idx
    if won:
        await _finish_with_prefix(query, mode, "card", True, "🎁 To'g'ri karta!\n\n")
    else:
        await query.edit_message_text(
            "😔 Bu safar omad kelmadi.\nYana urinib ko'ring!",
            reply_markup=_result_keyboard(mode, "card"),
            parse_mode="HTML",
        )


async def _act_slot(query, context, mode, rest):
    await query.answer()
    emojis = ["🍒", "🍋", "🔔", "💎", "⭐"]
    spin = [random.choice(emojis) for _ in range(3)]
    prefix = f"{' '.join(spin)}\n\n"
    won = spin[0] == spin[1] == spin[2]
    if won:
        await _finish_with_prefix(query, mode, "slot", True, prefix)
    else:
        await query.edit_message_text(
            prefix + "😔 Yutqazdingiz.",
            reply_markup=_result_keyboard(mode, "slot"),
            parse_mode="HTML",
        )


async def _act_chicken(query, context, mode, rest):
    choice = rest[0]
    await query.answer()
    result = random.choice(["tovuq", "tuxum"])
    won = choice == result
    label = "🐔 Tovuq" if result == "tovuq" else "🥚 Tuxum"
    prefix = f"Chiqdi: {label}\n\n"
    if won:
        await _finish_with_prefix(query, mode, "chicken", True, prefix)
    else:
        await query.edit_message_text(
            prefix + "😔 Bu safar omad kelmadi.\nYana urinib ko'ring!",
            reply_markup=_result_keyboard(mode, "chicken"),
            parse_mode="HTML",
        )


async def _act_quiz(query, context, mode, rest):
    correct, chosen = int(rest[0]), int(rest[1])
    await query.answer()
    won = correct == chosen
    if won:
        await _finish_with_prefix(query, mode, "quiz", True, "✅ To'g'ri javob!\n\n")
    else:
        await query.edit_message_text(
            "❌ Noto'g'ri javob.\nYana urinib ko'ring!",
            reply_markup=_result_keyboard(mode, "quiz"),
            parse_mode="HTML",
        )


async def _act_reflex(query, context, mode, rest):
    sub = rest[0]
    if sub == "ready":
        await query.answer()
        await query.edit_message_text("⏳ Tayyorlaning...", parse_mode="HTML")
        delay = random.uniform(1.5, 4.5)
        await asyncio.sleep(delay)
        start_ts = time.time()
        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔴 BOS!", callback_data=f"reflex:{mode}:hit:{start_ts}")]]
        )
        try:
            await query.edit_message_text("🔴 <b>BOS!</b>", reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
        return

    if sub == "hit":
        start_ts = float(rest[1])
        elapsed = time.time() - start_ts
        await query.answer()
        won = elapsed < 1.0
        prefix = f"⏱ Reaksiya vaqtingiz: {elapsed:.2f} soniya\n\n"
        if won:
            if mode == "paid":
                db.give_game_reward(_user_id(query), REWARD_AMOUNT)
                text = prefix + "⚡ <b>Juda tez!</b>\n🎉 Siz 10 💎 Almaz yutdingiz!"
            else:
                text = prefix + "⚡ <b>Juda tez!</b> ✅"
            await query.edit_message_text(text, reply_markup=_result_keyboard(mode, "reflex"), parse_mode="HTML")
        else:
            await query.edit_message_text(
                prefix + "😔 Sekin bosdingiz. Yana urinib ko'ring!",
                reply_markup=_result_keyboard(mode, "reflex"),
                parse_mode="HTML",
            )
        return

    await query.answer()


async def _act_number(query, context, mode, rest):
    # Faqat "bekor qilish" tugmasi shu yerdan keladi; taxminlar TEXT orqali.
    await query.answer()
    db.clear_number_game(_user_id(query))
    await query.edit_message_text(
        "❌ O'yin bekor qilindi.",
        reply_markup=_back_keyboard(mode),
        parse_mode="HTML",
    )


async def _finish_with_prefix(query, mode, key, won, prefix):
    if mode == "paid" and won:
        db.give_game_reward(_user_id(query), REWARD_AMOUNT)
        text = prefix + "🎉 <b>Tabriklaymiz!</b>\nSiz 10 💎 Almaz yutdingiz!"
    elif won:
        text = prefix + "✅ <b>Siz yutdingiz!</b> 🎉"
    else:
        text = prefix + "😔 Bu safar omad kelmadi.\nYana urinib ko'ring!"
    await query.edit_message_text(text, reply_markup=_result_keyboard(mode, key), parse_mode="HTML")


_ACTION_HANDLERS = {
    "mine": _act_mine,
    "target": _act_target,
    "dice": _act_dice,
    "coin": _act_coin,
    "card": _act_card,
    "slot": _act_slot,
    "chicken": _act_chicken,
    "quiz": _act_quiz,
    "reflex": _act_reflex,
    "number": _act_number,
}


# ---------------------------------------------------------------------------
# 🔢 Sonni top - matnli taxminlarni qabul qilish
# ---------------------------------------------------------------------------

async def receive_number_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = db.get_number_game(user_id)
    if not state:
        return  # Bu foydalanuvchi hozir bu o'yinda emas - e'tibor berilmaydi.

    text = (update.message.text or "").strip()
    if not text.isdigit():
        return

    guess = int(text)
    target = state["target"]
    mode = state["mode"]

    if guess == target:
        db.clear_number_game(user_id)
        if mode == "paid":
            db.give_game_reward(user_id, REWARD_AMOUNT)
            msg = f"🎉 <b>Tabriklaymiz!</b>\nTo'g'ri toptingiz: {target}!\nSiz 10 💎 Almaz yutdingiz!"
        else:
            msg = f"✅ <b>Siz yutdingiz!</b> 🎉\nTo'g'ri son: {target}"
        await update.message.reply_text(msg, reply_markup=_result_keyboard(mode, "number"), parse_mode="HTML")
        return

    tries_left = db.decrement_number_game_try(user_id)
    if tries_left <= 0:
        db.clear_number_game(user_id)
        await update.message.reply_text(
            f"😔 Urinishlar tugadi. Maxfiy son: {target} edi.\nYana urinib ko'ring!",
            reply_markup=_result_keyboard(mode, "number"),
            parse_mode="HTML",
        )
        return

    hint = "🔼 Kattaroq son o'ylang" if guess < target else "🔽 Kichikroq son o'ylang"
    await update.message.reply_text(
        f"❌ Noto'g'ri. {hint}.\nQolgan urinishlar: {tries_left}",
    )
