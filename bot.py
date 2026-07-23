# -*- coding: utf-8 -*-
"""
🎮 O'yin Sirlari — Free Fire Telegram bot
Asosiy ishga tushirish fayli.
"""

import logging
import re

from telegram import Update, MenuButtonDefault
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
    BTN_SETTINGS,
    BTN_NICKS,
    BTN_TABLET,
    BTN_HACK,
    BTN_CUSTOM_SETTING,
    BTN_WEBSITE,
    BTN_DIAMONDS,
    BTN_ACCOUNT,
    BTN_HELP,
    BTN_GUIDES,
    BTN_PREMIUM,
    BTN_STATS,
    BTN_BROADCAST,
    BTN_POST,
    BTN_EDIT_TEXTS,
)

from handlers.start import (
    start_command,
    check_subscription_callback,
    on_player_type_selected,
)
from handlers.menu import (
    haqida_command,
    menu_command,
    profil_command,
    yordam_command,
    yangiliklar_command,
    on_help_button,
    on_premium_button,
    on_website_button,
    on_settings_button,
    on_nicks_button,
    on_guides_button,
)
from handlers.hack import (
    on_hack_button,
    on_hack_proxy,
    on_hack_cheat,
    on_hack_back,
)
from handlers.settings import on_brand_selected, on_back_to_brands, on_model_selected
from handlers.tablet import (
    on_tablet_button,
    on_tablet_brand_selected,
    on_back_to_tablet_brands,
    on_tablet_model_selected,
)
from handlers.nicknames import on_nick_category, on_back_to_nicks
from handlers.guides import on_guide_selected, on_back_to_guides
from handlers.ffid import (
    start_ffid,
    receive_ff_id,
    cancel_ffid,
    cancel_ffid_to_hack,
    WAITING_FF_ID,
)
from handlers.custom_setting import (
    start_custom_setting,
    cancel_custom_setting,
    receive_custom_setting,
    WAITING_CUSTOM_REQUEST,
    start_custom_admin_reply,
    cancel_custom_admin_reply,
    receive_custom_admin_reply,
    WAITING_CUSTOM_ADMIN_REPLY,
)
from handlers.diamonds import (
    on_diamonds_button,
    on_diamonds_admin,
    on_diamonds_bot,
    on_diamonds_back,
    on_package_selected,
    start_buy,
    receive_order_ff_id,
    cancel_order,
    order_sent_by_admin,
    go_to_account_hint,
    on_account_button,
    on_account_admin,
    on_account_card,
    on_account_bonus,
    start_topup_paid,
    receive_topup_amount,
    receive_topup_receipt,
    cancel_topup,
    topup_approved,
    topup_rejected,
    WAITING_ORDER_FF_ID,
    WAITING_TOPUP_AMOUNT,
    WAITING_TOPUP_RECEIPT,
)
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
    start_edit_texts,
    choose_text_to_edit,
    receive_new_content,
    cancel_edit_text,
    WAITING_EDIT_TEXT,
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


async def post_init(application: Application):
    """Bot ishga tushganda - pastdagi 'Menu' (slash-buyruqlar) tugmasini olib tashlaydi."""
    try:
        await application.bot.set_my_commands([])
        await application.bot.set_chat_menu_button(menu_button=MenuButtonDefault())
    except Exception:
        pass


def build_application() -> Application:
    db.init_db()
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # ---------- Buyruqlar ----------
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("haqida", haqida_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("profil", profil_command))
    app.add_handler(CommandHandler("yordam", yordam_command))
    app.add_handler(CommandHandler("yangiliklar", yangiliklar_command))

    # ---------- Majburiy obuna tekshiruvi ----------
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(on_player_type_selected, pattern="^player:"))

    # ---------- FF ID conversation (Free Fire Hack menyusi orqali) ----------
    ffid_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_ffid, pattern="^hack:ffid$")],
        states={
            WAITING_FF_ID: [
                CommandHandler("bekor", cancel_ffid),
                CallbackQueryHandler(cancel_ffid_to_hack, pattern="^hack:back$"),
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

    # ---------- Matnlarni tahrirlash conversation (faqat admin, endi media ham qo'llab-quvvatlaydi) ----------
    edit_texts_conv = ConversationHandler(
        entry_points=[MessageHandler(_exact(BTN_EDIT_TEXTS), start_edit_texts)],
        states={
            WAITING_EDIT_TEXT: [
                CommandHandler("bekor", cancel_edit_text),
                MessageHandler(
                    (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL)
                    & ~filters.COMMAND,
                    receive_new_content,
                ),
            ],
        },
        fallbacks=[CommandHandler("bekor", cancel_edit_text)],
    )
    app.add_handler(CallbackQueryHandler(choose_text_to_edit, pattern="^edittext:"))
    app.add_handler(edit_texts_conv)

    # ---------- Alohida nastroyka so'rovi (foydalanuvchi tomondan) ----------
    custom_setting_conv = ConversationHandler(
        entry_points=[MessageHandler(_exact(BTN_CUSTOM_SETTING), start_custom_setting)],
        states={
            WAITING_CUSTOM_REQUEST: [
                CommandHandler("bekor", cancel_custom_setting),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_custom_setting),
            ],
        },
        fallbacks=[CommandHandler("bekor", cancel_custom_setting)],
    )
    app.add_handler(custom_setting_conv)

    # ---------- Alohida nastroyka - admin javobi (matn/rasm/video) ----------
    custom_admin_reply_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_custom_admin_reply, pattern="^customreply:")],
        states={
            WAITING_CUSTOM_ADMIN_REPLY: [
                CommandHandler("bekor", cancel_custom_admin_reply),
                MessageHandler(
                    (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL)
                    & ~filters.COMMAND,
                    receive_custom_admin_reply,
                ),
            ],
        },
        fallbacks=[CommandHandler("bekor", cancel_custom_admin_reply)],
    )
    app.add_handler(custom_admin_reply_conv)

    # ---------- Almaz sotib olish (xarid) conversation ----------
    buy_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_buy, pattern="^buy:")],
        states={
            WAITING_ORDER_FF_ID: [
                CommandHandler("bekor", cancel_order),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_order_ff_id),
            ],
        },
        fallbacks=[CommandHandler("bekor", cancel_order)],
    )
    app.add_handler(buy_conv)

    # ---------- Hisobim to'ldirish (to'lov) conversation ----------
    topup_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_topup_paid, pattern="^topup:paid$")],
        states={
            WAITING_TOPUP_AMOUNT: [
                CommandHandler("bekor", cancel_topup),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_topup_amount),
            ],
            WAITING_TOPUP_RECEIPT: [
                CommandHandler("bekor", cancel_topup),
                MessageHandler(filters.PHOTO & ~filters.COMMAND, receive_topup_receipt),
            ],
        },
        fallbacks=[CommandHandler("bekor", cancel_topup)],
    )
    app.add_handler(topup_conv)

    # ---------- Reply tugmalar ----------
    app.add_handler(MessageHandler(_exact(BTN_HELP), on_help_button))
    app.add_handler(MessageHandler(_exact(BTN_SETTINGS), on_settings_button))
    app.add_handler(MessageHandler(_exact(BTN_NICKS), on_nicks_button))
    app.add_handler(MessageHandler(_exact(BTN_TABLET), on_tablet_button))
    app.add_handler(MessageHandler(_exact(BTN_GUIDES), on_guides_button))
    app.add_handler(MessageHandler(_exact(BTN_PREMIUM), on_premium_button))
    app.add_handler(MessageHandler(_exact(BTN_HACK), on_hack_button))
    app.add_handler(MessageHandler(_exact(BTN_WEBSITE), on_website_button))
    app.add_handler(MessageHandler(_exact(BTN_STATS), on_stats_button))
    app.add_handler(MessageHandler(_exact(BTN_DIAMONDS), on_diamonds_button))
    app.add_handler(MessageHandler(_exact(BTN_ACCOUNT), on_account_button))

    # ---------- Inline callbacklar: Nastroykalar (telefon) ----------
    app.add_handler(CallbackQueryHandler(on_brand_selected, pattern="^brand:"))
    app.add_handler(CallbackQueryHandler(on_back_to_brands, pattern="^back_to_brands$"))
    app.add_handler(CallbackQueryHandler(on_model_selected, pattern="^model:"))

    # ---------- Inline callbacklar: Planshet nastroykalari ----------
    app.add_handler(CallbackQueryHandler(on_tablet_brand_selected, pattern="^tbrand:"))
    app.add_handler(CallbackQueryHandler(on_back_to_tablet_brands, pattern="^back_to_tbrands$"))
    app.add_handler(CallbackQueryHandler(on_tablet_model_selected, pattern="^tmodel:"))

    # ---------- Inline callbacklar: Niklar ----------
    app.add_handler(CallbackQueryHandler(on_nick_category, pattern="^nick:"))
    app.add_handler(CallbackQueryHandler(on_back_to_nicks, pattern="^back_to_nicks$"))

    # ---------- Inline callbacklar: Qo'llanmalar ----------
    app.add_handler(CallbackQueryHandler(on_guide_selected, pattern="^guide:"))
    app.add_handler(CallbackQueryHandler(on_back_to_guides, pattern="^back_to_guides$"))

    # ---------- Inline callbacklar: Almaz sotib olish ----------
    app.add_handler(CallbackQueryHandler(on_diamonds_admin, pattern="^dia:admin$"))
    app.add_handler(CallbackQueryHandler(on_diamonds_bot, pattern="^dia:bot$"))
    app.add_handler(CallbackQueryHandler(on_diamonds_back, pattern="^dia:back$"))
    app.add_handler(CallbackQueryHandler(on_package_selected, pattern="^pkg:"))
    app.add_handler(CallbackQueryHandler(order_sent_by_admin, pattern="^order_sent:"))
    app.add_handler(CallbackQueryHandler(go_to_account_hint, pattern="^go_account$"))

    # ---------- Inline callbacklar: Hisobim ----------
    app.add_handler(CallbackQueryHandler(on_account_admin, pattern="^acc:admin$"))
    app.add_handler(CallbackQueryHandler(on_account_card, pattern="^acc:card$"))
    app.add_handler(CallbackQueryHandler(on_account_bonus, pattern="^acc:bonus$"))
    app.add_handler(CallbackQueryHandler(topup_approved, pattern="^topup_ok:"))
    app.add_handler(CallbackQueryHandler(topup_rejected, pattern="^topup_no:"))

    # ---------- Inline callbacklar: Free Fire Hack (proxy/cheat; ffid alohida conv orqali) ----------
    app.add_handler(CallbackQueryHandler(on_hack_proxy, pattern="^hack:proxy$"))
    app.add_handler(CallbackQueryHandler(on_hack_cheat, pattern="^hack:cheat$"))
    app.add_handler(CallbackQueryHandler(on_hack_back, pattern="^hack:back$"))

    # ---------- Statistika uchun umumiy loglash (barcha xabarlar) ----------
    app.add_handler(MessageHandler(filters.ALL, log_all_messages), group=1)

    return app


def main():
    app = build_application()
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
