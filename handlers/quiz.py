# -*- coding: utf-8 -*-
"""🧠 Savol va Javob - Free Fire viktorinasi. To'g'ri javob uchun almaz beriladi."""

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from data.quiz_data import QUESTIONS
from keyboards import quiz_options_keyboard

DAILY_LIMIT = 3
REWARD_PER_CORRECT = 2


def _pick_question_index(answered_today: int) -> int:
    return answered_today % len(QUESTIONS)


async def _send_question(message_target, user_id: int, edit: bool = False):
    answered = db.get_quiz_answered_today(user_id)
    q_index = _pick_question_index(answered)
    question = QUESTIONS[q_index]

    text = (
        "🧠 <b>Savol va Javob</b>\n\n"
        f"📊 Bugungi savol: {answered + 1}/{DAILY_LIMIT}\n\n"
        f"❓ {question['question']}"
    )
    markup = quiz_options_keyboard(q_index, question["options"])

    if edit:
        await message_target.edit_message_text(text, parse_mode="HTML", reply_markup=markup)
    else:
        await message_target.reply_text(text, parse_mode="HTML", reply_markup=markup)


async def on_quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    answered = db.get_quiz_answered_today(user_id)

    if answered >= DAILY_LIMIT:
        total = db.get_quiz_diamonds(user_id)
        await update.message.reply_text(
            "✅ <b>Bugungi 3 ta savolingizga javob berib bo'ldingiz!</b>\n\n"
            f"💎 Jami yig'ilgan almazlaringiz: <b>{total}</b>\n\n"
            "Ertaga qayta urinib ko'ring.",
            parse_mode="HTML",
        )
        return

    await _send_question(update.message, user_id, edit=False)


async def on_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    parts = query.data.split(":")
    q_index = int(parts[1])
    chosen = int(parts[2])

    answered_before = db.get_quiz_answered_today(user_id)
    if answered_before >= DAILY_LIMIT:
        await query.answer("Bugungi savollaringiz tugagan, ertaga urinib ko'ring.", show_alert=True)
        return

    await query.answer()
    question = QUESTIONS[q_index]
    is_correct = chosen == question["correct"]

    db.increment_quiz_answered(user_id)
    if is_correct:
        db.add_quiz_diamonds(user_id, REWARD_PER_CORRECT)
        result_text = f"✅ <b>To'g'ri javob!</b> +{REWARD_PER_CORRECT} 💎"
    else:
        correct_text = question["options"][question["correct"]]
        result_text = f"❌ <b>Noto'g'ri.</b> To'g'ri javob: {correct_text}"

    answered_after = db.get_quiz_answered_today(user_id)
    total = db.get_quiz_diamonds(user_id)

    if answered_after >= DAILY_LIMIT:
        await query.edit_message_text(
            f"{result_text}\n\n"
            f"🏁 Bugungi 3 ta savolingiz tugadi!\n"
            f"💎 Jami yig'ilgan almazlaringiz: <b>{total}</b>\n\n"
            "Ertaga qayta urinib ko'ring.",
            parse_mode="HTML",
        )
        return

    await query.edit_message_text(
        f"{result_text}\n\n💎 Jami: <b>{total}</b>", parse_mode="HTML"
    )
    await _send_question(query.message, user_id, edit=False)
