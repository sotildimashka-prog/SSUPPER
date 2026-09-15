import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# Handler va zarur funksiyani import qilish
from handlers.withdraw import process_withdraw_request, on_withdraw_sent_by_admin

# Bot tokeningiz
BOT_TOKEN = "YOUR_BOT_TOKEN"

def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Buyruqlar va callback handlerlarni ulash
    app.add_handler(CommandHandler("withdraw", process_withdraw_request))
    app.add_handler(CallbackQueryHandler(on_withdraw_sent_by_admin, pattern="^withdraw_approve"))

    # Botni ishga tushirish
    app.run_polling()

if __name__ == "__main__":
    main()
