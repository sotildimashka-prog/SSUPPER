# -*- coding: utf-8 -*-
"""
🎮 O'yin Sirlari — Free Fire Telegram bot
Asosiy ishga tushirish fayli.
"""

import logging
import re

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

import database as db
from config import BOT_TOKEN
from keyboards import (
    BTN_HELP,
    BTN_SETTINGS,
    BTN_NICKS,
    BTN_GUIDES,
    BTN_PREMIUM,
    BTN_CHEAT,
    BTN_FFID,
    BTN_PROXY,
    BTN_STATS,
    BTN_BROADCAST,
    BTN_POST,
)

from handlers.start import start_command, check_subscription_callback
from handlers.menu import (
    haqida_command,
    menu_command,
    profil_command,
    yordam_command,
    yangiliklar_command,
    on_help_button,
    on_premium_button,
    on_cheat_button,
    on_proxy_button,
    on_settings_button,
    on_nicks_button,
    on_guides_button,
)
from handlers.settings import on_brand_selected, on_back_to_brands, on_model_selected
from handlers.nicknames import on_nick_category, on_back_to_nicks
from handlers.guides import on_guide_selected, on_back_to_guides
from handlers.ffid import start_ffid, receive_ff_id, cancel_ffid, WAITING_FF_ID
from handlers.admin import (
    on_stats_button,
    start_broadcast,
    send_broadcast,
    cancel_broadcast,
    WAITING_BROADCAST,
    start_post,
    receive_post_text,
    receive_post_button,
    skip_post_button,
    cancel_post,
    WAITING_POST_TEXT,
    WAITING_POST_BUTTON,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _exact(text: str):
    return filters.Regex(f"^{re.escape(text)}$")


async def log_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Har qanday matnli xabarni statistikaga yozib boradi (bloklamaydi)."""
    if update.effective_user:
        db.touch_user_activity(update.effective_user.id)
        db.log_message(update.effective_user.id)


def build_application() -> Application:
    db.init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # ---------- Buyruqlar ----------
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("haqida", haqida_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("profil", profil_command))
    app.add_handler(CommandHandler("yordam", yordam_command))
    app.add_handler(CommandHandler("yangiliklar", yangiliklar_command))

    # ---------- Majburiy obuna tekshiruvi ----------
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$"))

    # ---------- FF ID conversation ----------
    ffid_conv = ConversationHandler(
        entry_points=[MessageHandler(_exact(BTN_FFID), start_ffid)],
        states={
            WAITING_FF_ID: [
                CommandHandler("bekor", cancel_ffid),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_ff_id),
            ]
        },
        fallbacks=[CommandHandler("bekor", cancel_ffid)],
    )
    app.add_handler(ffid_conv)

    # ---------- Broadcast conversation (faqat admin) ----------
    broadcast_conv = ConversationHandler(
        entry_points=[MessageHandler(_exact(BTN_BROADCAST), start_broadcast)],
        states={
            WAITING_BROADCAST: [
                CommandHandler("bekor", cancel_broadcast),
                MessageHandler(filters.ALL & ~filters.COMMAND, send_broadcast),
            ]
        },
        fallbacks=[CommandHandler("bekor", cancel_broadcast)],
    )
    app.add_handler(broadcast_conv)

    # ---------- Post conversation (faqat admin) ----------
    post_conv = ConversationHandler(
        entry_points=[MessageHandler(_exact(BTN_POST), start_post)],
        states={
            WAITING_POST_TEXT: [
                CommandHandler("bekor", cancel_post),
                MessageHandler(
                    (filters.TEXT | filters.PHOTO) & ~filters.COMMAND, receive_post_text
                ),
            ],
            WAITING_POST_BUTTON: [
                CommandHandler("bekor", cancel_post),
                CommandHandler("otkazib_yuborish", skip_post_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_post_button),
            ],
        },
        fallbacks=[CommandHandler("bekor", cancel_post)],
    )
    app.add_handler(post_conv)

    # ---------- Reply tugmalar ----------
    app.add_handler(MessageHandler(_exact(BTN_HELP), on_help_button))
    app.add_handler(MessageHandler(_exact(BTN_SETTINGS), on_settings_button))
    app.add_handler(MessageHandler(_exact(BTN_NICKS), on_nicks_button))
    app.add_handler(MessageHandler(_exact(BTN_GUIDES), on_guides_button))
    app.add_handler(MessageHandler(_exact(BTN_PREMIUM), on_premium_button))
    app.add_handler(MessageHandler(_exact(BTN_CHEAT), on_cheat_button))
    app.add_handler(MessageHandler(_exact(BTN_PROXY), on_proxy_button))
    app.add_handler(MessageHandler(_exact(BTN_STATS), on_stats_button))

    # ---------- Inline callbacklar: Nastroykalar ----------
    app.add_handler(CallbackQueryHandler(on_brand_selected, pattern="^brand:"))
    app.add_handler(CallbackQueryHandler(on_back_to_brands, pattern="^back_to_brands$"))
    app.add_handler(CallbackQueryHandler(on_model_selected, pattern="^model:"))

    # ---------- Inline callbacklar: Niklar ----------
    app.add_handler(CallbackQueryHandler(on_nick_category, pattern="^nick:"))
    app.add_handler(CallbackQueryHandler(on_back_to_nicks, pattern="^back_to_nicks$"))

    # ---------- Inline callbacklar: Qo'llanmalar ----------
    app.add_handler(CallbackQueryHandler(on_guide_selected, pattern="^guide:"))
    app.add_handler(CallbackQueryHandler(on_back_to_guides, pattern="^back_to_guides$"))

    # ---------- Statistika uchun umumiy loglash (barcha xabarlar) ----------
    app.add_handler(MessageHandler(filters.ALL, log_all_messages), group=1)

    return app


def main():
    app = build_application()
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
