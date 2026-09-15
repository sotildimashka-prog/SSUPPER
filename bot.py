import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode

# Handlerlarni import qilish
from handlers import withdraw
# Logdagi xatolik yo'qolishi uchun shu funksiya import qilinadi:
from handlers.withdraw import on_withdraw_sent_by_admin

# Bot tokeningiz (Railway yoki .env fayldan olinadi)
BOT_TOKEN = "YOUR_BOT_TOKEN"

async def main():
    # Loglarni sozlash
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(withdraw.router)

    # Admin to'lovni tasdiqlaganda ishlaydigan callback-handlerni ro'yxatdan o'tkazish
    dp.callback_query.register(on_withdraw_sent_by_admin, F.data.startswith("withdraw_approve"))

    # Eskirgan xabarlarni o'tkazib yuborish va botni ishga tushirish
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
