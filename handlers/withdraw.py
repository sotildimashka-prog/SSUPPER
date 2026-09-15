from telegram import Update
from telegram.ext import ContextTypes

# 1. Foydalanuvchi pul yechish tugmasini bosganda
async def process_withdraw_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Pul yechib olish uchun miqdor va karta raqamingizni kiriting.")

# 2. Admin pul yechish so'rovini tasdiqlaganda ishlaydigan funksiya
async def on_withdraw_sent_by_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer("To'lov administrator tomonidan tasdiqlandi!", show_alert=True)
        await query.edit_message_text("✅ Ushbu to'lov so'rovi muvaffaqiyatli bajarildi.")
