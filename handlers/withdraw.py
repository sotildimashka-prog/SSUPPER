from telegram import Update
from telegram.ext import ContextTypes
from database import get_user

async def withdraw_diamonds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    user = get_user(user_id)
    balance = user[1] if user else 0
    referrals_count = user[3] if user else 0

    if balance < 190:
        text = (
            "❌ **Hali 190 almazga yetmadi!**\n\n"
            "💎 Almazlaringizni yana ko‘paytiring va 190 taga yetkazing.\n"
            "🚀 Shoshilmang, yana ozgina qoldi!"
        )
    else:
        if referrals_count < 10:
            bot_username = (await context.bot.get_me()).username
            ref_link = f"https://t.me/{bot_username}?start={user_id}"
            text = (
                "🎉 **OFARIN!**\n"
                "💎 Siz 190 almazni yig‘ishga muvaffaq bo‘ldingiz!\n"
                "🔥 Juda yaxshi natija! Endi almazlaringizni yechib olishingiz mumkin.\n\n"
                "👥 **Almazlarni yechib olish uchun 10 ta do‘stingizni botga taklif qiling!**\n"
                "🔗 10 ta do‘stingiz botga kirib /start bosgandan so‘ng, almazlarni yechib olish imkoniyati ochiladi.\n\n"
                f"Sizning referal havolangiz:\n`{ref_link}`\n\n"
                f"Hozirgi taklif qilgan do‘stlaringiz: **{referrals_count}/10**"
            )
        else:
            text = "✅ **Tabriklaymiz!** 10 ta referal yig‘ildi. Almazlarni yechish uchun hamyon manzilingizni yuboring."

    await query.edit_message_text(text, parse_mode="Markdown")
