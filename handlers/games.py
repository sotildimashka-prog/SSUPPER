import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_user, add_diamonds

QUESTIONS = [
    {"q": "O‘zbekiston Respublikasining poytaxti qaysi shahar?", "options": ["Toshkent", "Samarqand", "Buxoro"], "ans": "Toshkent"},
    {"q": "1 yilda necha oy bor?", "options": ["10", "12", "14"], "ans": "12"},
    {"q": "Qaysi sayyora Qizil sayyora deb ataladi?", "options": ["Venera", "Mars", "Yupiter"], "ans": "Mars"},
    {"q": "5 + 7 nechaga teng?", "options": ["11", "12", "13"], "ans": "12"}
]

async def games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🎮 **O‘YINLAR VA MUKOFOT TIZIMI**\n\n"
        "✨ **Oson o‘yinlarda** kamroq almaz ishlanadi.\n"
        "🔥 **Qiyin o‘yinlarda** 5 almazgacha mukofot beriladi!\n\n"
        "O‘yiningizni tanlang:"
    )
    keyboard = [
        [InlineKeyboardButton("🎮 Oson o‘yin", callback_data="easy_game"), InlineKeyboardButton("🔥 Qiyin o‘yin", callback_data="hard_game")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def easy_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    question_data = random.choice(QUESTIONS)
    opts = question_data["options"][:]
    random.shuffle(opts)

    keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{'1' if opt == question_data['ans'] else '0'}")] for opt in opts]
    await query.edit_message_text(f"🧠 **Oson Viktorina:**\n\n{question_data['q']}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "ans_1":
        add_diamonds(user_id, 2)
        text = "🎉 To‘g‘ri javob! Sizga **+2 almaz** berildi."
    else:
        add_diamonds(user_id, -2)
        text = "❌ Noto‘g‘ri javob! Sizdan **-2 almaz** ayirildi."

    keyboard = [[InlineKeyboardButton("🔄 Yana o‘ynash", callback_data="easy_game")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def hard_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    reward = random.randint(3, 5)
    add_diamonds(query.from_user.id, reward)
    text = f"🔥 **Qiyin o‘yin topshirig‘i bajarildi!**\n\nSiz **+{reward} almaz** yutib oldingiz!"
    keyboard = [[InlineKeyboardButton("🔄 Yana o‘ynash", callback_data="hard_game")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
