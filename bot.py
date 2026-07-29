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
    BTN_CUSTOM,
    BTN_WEBSITE,
    BTN_NEWS,
    BTN_MUSIC,
    BTN_QUIZ,
    BTN_DIAMONDS,
    BTN_ACCOUNT,
    BTN_HELP,
    BTN_GUIDES,
    BTN_FAQ,
    BTN_STATS,
    BTN_BROADCAST,
    BTN_POST,
    BTN_EDIT_TEXTS,
    BTN_ADMIN_CREDIT,
    BTN_WITHDRAW,
    BTN_GIFT_ALL,
    BTN_FF2017,
    BTN_MAIN_FF,
    BTN_MAIN_DIAMONDS,
    BTN_MAIN_SERVICES,
    BTN_MAIN_PROFILE,
    BTN_M2_DIAMONDS,
    BTN_M2_SERVICES,
    BTN_M2_SETTINGS,
    BTN_M2_NICKS,
    BTN_M2_PAYMENTS,
    BTN_GIFTS,
)

from handlers.start import (
    start_command,
    check_subscription_callback,
    on_player_type_selected,
    on_language_selected,
)
from handlers.gifts import (
    on_gifts_button,
    on_gift_free_diamond,
    on_gift_money_bonus,
    on_gift_diamond_bonus,
)
from handlers.menu import (
    haqida_command,
    menu_command,
    profil_command,
    yordam_command,
    yangiliklar_command,
    saytimiz_command,
    on_help_button,
    on_settings_button,
    on_nicks_button,
    on_guides_button,
    on_website_button,
    on_news_button,
    on_music_button,
    on_ff2017_button,
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
from handlers.hack import (
    on_hack_button,
    on_hack_back,
    on_hack_proxy,
    on_hack_cheat,
    on_hack_ffid,
    receive_ff_id,
    cancel_ffid,
    WAITING_FF_ID,
)
from handlers.faq import (
    start_faq,
    start_faq_from_callback,
    receive_faq_question,
    cancel_faq,
    start_faq_admin_reply,
    receive_faq_admin_reply,
    cancel_faq_admin_reply,
    WAITING_FAQ_QUESTION,
    WAITING_FAQ_ADMIN_REPLY,
)
from handlers.quiz import on_quiz_button, on_quiz_button_callback, on_quiz_answer, on_quiz_begin
from handlers.custom import (
    on_custom_button,
    on_custom_back,
    on_custom_free,
    cancel_free,
    receive_free_model,
    on_custom_paid,
    on_paid_tier_selected,
    on_paid_buy_clicked,
    on_paid_agree,
    cancel_paid,
    receive_paid_model,
    start_custom_admin_reply,
    receive_custom_admin_reply,
    cancel_custom_admin_reply,
    WAITING_FREE_MODEL,
    WAITING_PAID_MODEL,
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
    on_account_back,
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
    receive_new_text,
    cancel_edit_text,
    WAITING_EDIT_TEXT,
)
from handlers.admin_credit import (
    on_admin_credit_button,
    on_credit_type_selected,
    receive_credit_amount,
    receive_credit_user_id,
    cancel_credit,
    WAITING_CREDIT_AMOUNT,
    WAITING_CREDIT_USER_ID,
    on_gift_all_button,
    on_gift_type_selected,
    receive_gift_amount,
    on_gift_all_confirm,
    on_gift_all_cancel,
    WAITING_GIFT_AMOUNT,
)
from handlers.withdraw import (
    on_withdraw_button,
    on_withdraw_button_callback,
    on_withdraw_amount_confirm,
    receive_withdraw_ff_id,
    cancel_withdraw,
    WAITING_WITHDRAW_FF_ID,
)

# ---------- Yangi bosh menyu bo'limlari (🎮 Free Fire / 💎 Almaz olish / 🛠️ Xizmatlar / 👤 Profil) ----------
from handlers.ffmenu import (
    on_ff_main_button,
    on_back_to_ff,
    on_ff_phone,
    on_ff_tablet,
    on_ff_pc,
)
from handlers.pc import on_pc_model_selected, on_back_to_pc
from handlers.nickgen import (
    start_nick_creation,
    receive_nick_name,
    cancel_nick_creation,
    WAITING_NICK_NAME,
)
from handlers.services import (
    on_services_button,
    on_back_to_services,
    on_svc_bonus,
    on_svc_pay,
    on_svc_guides,
    on_svc_news,
    on_svc_other,
    on_back_to_services_other,
    on_svcother_help,
    on_svcother_website,
    on_svcother_music,
    on_svcother_hack,
    on_svcother_custom,
    on_svcother_ff2017,
)
from handlers.profile import on_profile_button, on_profile_account

# ---------- 🆕 Yangi asosiy menyu (6 tugma, 2 ustunda) ----------
from handlers.newflow import (
    on_m2_diamonds_button,
    on_diaget_free,
    on_diaget_buy,
    on_m2_settings_button,
    on_newset_back,
    on_newset_premium,
    on_m2_nicks_button,
    on_newnick_back,
    on_newnick_category,
    on_m2_services_button,
    on_newsvc_back,
    on_newsvc_item,
    on_m2_payments_button,
    on_pay_back,
    on_pay_bonus_diamond,
    on_pay_daily_bonus,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _exact(text: str):
    return filters.Regex(f"^{re.escape(text)}$")


async def log_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        db.touch_user_activity(update.effective_user.id)
        db.log_message(update.effective_user.id)


async def post_init(application: Application):
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
    app.add_handler(CommandHandler("saytimiz", saytimiz_command))

    # ---------- 🌐 Til tanlash ----------
    app.add_handler(CallbackQueryHandler(on_language_selected, pattern="^lang:"))

    # ---------- Majburiy obuna tekshiruvi ----------
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(on_player_type_selected, pattern="^player:"))

    # ---------- 🔓 Maxsus xizmat (Proxy/Cheat/FF ID) ----------
    hack_ffid_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(on_hack_ffid, pattern="^hack:ffid$")],
        states={
            WAITING_FF_ID: [
                CommandHandler("bekor", cancel_ffid),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_ff_id),
            ]
        },
        fallbacks=[CommandHandler("bekor", cancel_ffid)],
    )
    app.add_handler(hack_ffid_conv)
    app.add_handler(CallbackQueryHandler(on_hack_proxy, pattern="^hack:proxy$"))
    app.add_handler(CallbackQueryHandler(on_hack_cheat, pattern="^hack:cheat$"))
    app.add_handler(CallbackQueryHandler(on_hack_back, pattern="^hack:back$"))

    # ---------- 📬 Savollar (FAQ) ----------
    faq_conv = ConversationHandler(
        entry_points=[
            MessageHandler(_exact(BTN_FAQ), start_faq),
            CallbackQueryHandler(start_faq_from_callback, pattern="^svc:faq$"),
        ],
        states={
            WAITING_FAQ_QUESTION: [
                CommandHandler("bekor", cancel_faq),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_faq_question),
            ]
        },
        fallbacks=[CommandHandler("bekor", cancel_faq)],
    )
    app.add_handler(faq_conv)

    faq_admin_reply_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_faq_admin_reply, pattern="^faqreply:")],
        states={
            WAITING_FAQ_ADMIN_REPLY: [
                CommandHandler("bekor", cancel_faq_admin_reply),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_faq_admin_reply),
            ]
        },
        fallbacks=[CommandHandler("bekor", cancel_faq_admin_reply)],
    )
    app.add_handler(faq_admin_reply_conv)

    # ---------- 📲 Shaxsiy nastroyka (Pullik / Bepul) ----------
    custom_free_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(on_custom_free, pattern="^custom:free$")],
        states={
            WAITING_FREE_MODEL: [
                CommandHandler("bekor", cancel_free),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_free_model),
            ]
        },
        fallbacks=[CommandHandler("bekor", cancel_free)],
    )
    app.add_handler(custom_free_conv)

    custom_paid_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(on_paid_agree, pattern="^paidagree:")],
        states={
            WAITING_PAID_MODEL: [
                CommandHandler("bekor", cancel_paid),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_paid_model),
            ]
        },
        fallbacks=[CommandHandler("bekor", cancel_paid)],
    )
    app.add_handler(custom_paid_conv)

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
            ]
        },
        fallbacks=[CommandHandler("bekor", cancel_custom_admin_reply)],
    )
    app.add_handler(custom_admin_reply_conv)

    app.add_handler(MessageHandler(_exact(BTN_CUSTOM), on_custom_button))
    app.add_handler(CallbackQueryHandler(on_custom_back, pattern="^custom:back$"))
    app.add_handler(CallbackQueryHandler(on_custom_paid, pattern="^custom:paid$"))
    app.add_handler(CallbackQueryHandler(on_paid_tier_selected, pattern="^paidtier:"))
    app.add_handler(CallbackQueryHandler(on_paid_buy_clicked, pattern="^paidbuy:"))

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

    # ---------- Matnlarni tahrirlash conversation (faqat admin) ----------
    edit_texts_conv = ConversationHandler(
        entry_points=[MessageHandler(_exact(BTN_EDIT_TEXTS), start_edit_texts)],
        states={
            WAITING_EDIT_TEXT: [
                CommandHandler("bekor", cancel_edit_text),
                MessageHandler(
                    (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL)
                    & ~filters.COMMAND,
                    receive_new_text,
                ),
            ],
        },
        fallbacks=[CommandHandler("bekor", cancel_edit_text)],
    )
    app.add_handler(CallbackQueryHandler(choose_text_to_edit, pattern="^edittext:"))
    app.add_handler(edit_texts_conv)

    # ---------- 🛠 Admin buyrug'i (qo'lda pul/almaz berish, faqat admin) ----------
    app.add_handler(MessageHandler(_exact(BTN_ADMIN_CREDIT), on_admin_credit_button))

    admin_credit_flow_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(on_credit_type_selected, pattern="^credittype:")],
        states={
            WAITING_CREDIT_AMOUNT: [
                CommandHandler("bekor", cancel_credit),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_credit_amount),
            ],
            WAITING_CREDIT_USER_ID: [
                CommandHandler("bekor", cancel_credit),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_credit_user_id),
            ],
        },
        fallbacks=[CommandHandler("bekor", cancel_credit)],
    )
    app.add_handler(admin_credit_flow_conv)

    # ---------- 🎁 Hammaga sovg'a (barcha foydalanuvchilarga birdaniga, faqat admin) ----------
    app.add_handler(MessageHandler(_exact(BTN_GIFT_ALL), on_gift_all_button))

    gift_all_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(on_gift_type_selected, pattern="^giftall:")],
        states={
            WAITING_GIFT_AMOUNT: [
                CommandHandler("bekor", cancel_credit),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_gift_amount),
            ],
        },
        fallbacks=[CommandHandler("bekor", cancel_credit)],
    )
    app.add_handler(gift_all_conv)
    app.add_handler(CallbackQueryHandler(on_gift_all_confirm, pattern="^giftall_confirm$"))
    app.add_handler(CallbackQueryHandler(on_gift_all_cancel, pattern="^giftall_cancel$"))

    # ---------- 💎 Almaz yechish (Tekin almazdan yig'ilganini yechib olish) ----------
    app.add_handler(MessageHandler(_exact(BTN_WITHDRAW), on_withdraw_button))
    withdraw_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(on_withdraw_amount_confirm, pattern="^withdraw_confirm:")],
        states={
            WAITING_WITHDRAW_FF_ID: [
                CommandHandler("bekor", cancel_withdraw),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_withdraw_ff_id),
            ],
        },
        fallbacks=[CommandHandler("bekor", cancel_withdraw)],
    )
    app.add_handler(withdraw_conv)

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
    app.add_handler(MessageHandler(_exact(BTN_WEBSITE), on_website_button))
    app.add_handler(MessageHandler(_exact(BTN_FF2017), on_ff2017_button))
    app.add_handler(MessageHandler(_exact(BTN_NEWS), on_news_button))
    app.add_handler(MessageHandler(_exact(BTN_MUSIC), on_music_button))
    app.add_handler(MessageHandler(_exact(BTN_QUIZ), on_quiz_button))
    app.add_handler(CallbackQueryHandler(on_quiz_begin, pattern="^quiz_begin$"))
    app.add_handler(CallbackQueryHandler(on_quiz_answer, pattern="^quiz:"))
    app.add_handler(MessageHandler(_exact(BTN_HACK), on_hack_button))
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
    app.add_handler(CallbackQueryHandler(on_account_back, pattern="^acc:back$"))
    app.add_handler(CallbackQueryHandler(topup_approved, pattern="^topup_ok:"))
    app.add_handler(CallbackQueryHandler(topup_rejected, pattern="^topup_no:"))

    # ============================================================================
    # 🆕 Yangi bosh menyu (faqat 4 ta tugma): 🎮 Free Fire / 💎 Almaz olish /
    # 🛠️ Xizmatlar / 👤 Profil
    # ============================================================================

    # ---------- 🎮 Free Fire (reply tugma + inline bo'limlar) ----------
    app.add_handler(MessageHandler(_exact(BTN_MAIN_FF), on_ff_main_button))
    app.add_handler(CallbackQueryHandler(on_back_to_ff, pattern="^back_to_ff$"))
    app.add_handler(CallbackQueryHandler(on_ff_phone, pattern="^ffmenu:phone$"))
    app.add_handler(CallbackQueryHandler(on_ff_tablet, pattern="^ffmenu:tablet$"))
    app.add_handler(CallbackQueryHandler(on_ff_pc, pattern="^ffmenu:pc$"))

    # ---------- 💻 PC nastroyka (20 ta model) ----------
    app.add_handler(CallbackQueryHandler(on_pc_model_selected, pattern="^pc:"))
    app.add_handler(CallbackQueryHandler(on_back_to_pc, pattern="^back_to_pc$"))

    # ---------- 🎮 Nik yaratish (ism -> 20+ nik) ----------
    nick_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_nick_creation, pattern="^ffmenu:nick$")],
        states={
            WAITING_NICK_NAME: [
                CommandHandler("bekor", cancel_nick_creation),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_nick_name),
            ]
        },
        fallbacks=[CommandHandler("bekor", cancel_nick_creation)],
    )
    app.add_handler(nick_conv)

    # ---------- 💎 Almaz olish (reply tugma - eski Almaz sotib olish oqimi qayta ishlatiladi) ----------
    app.add_handler(MessageHandler(_exact(BTN_MAIN_DIAMONDS), on_diamonds_button))

    # ---------- 🛠️ Xizmatlar (reply tugma + inline bo'limlar) ----------
    app.add_handler(MessageHandler(_exact(BTN_MAIN_SERVICES), on_services_button))
    app.add_handler(CallbackQueryHandler(on_back_to_services, pattern="^back_to_services$"))
    app.add_handler(CallbackQueryHandler(on_svc_bonus, pattern="^svc:bonus$"))
    app.add_handler(CallbackQueryHandler(on_svc_pay, pattern="^svc:pay$"))
    app.add_handler(CallbackQueryHandler(on_svc_guides, pattern="^svc:guides$"))
    app.add_handler(CallbackQueryHandler(on_svc_news, pattern="^svc:news$"))
    app.add_handler(CallbackQueryHandler(on_svc_other, pattern="^svc:other$"))
    app.add_handler(CallbackQueryHandler(on_back_to_services_other, pattern="^back_to_svcother$"))
    app.add_handler(CallbackQueryHandler(on_svcother_help, pattern="^svcother:help$"))
    app.add_handler(CallbackQueryHandler(on_svcother_website, pattern="^svcother:website$"))
    app.add_handler(CallbackQueryHandler(on_svcother_music, pattern="^svcother:music$"))
    app.add_handler(CallbackQueryHandler(on_svcother_hack, pattern="^svcother:hack$"))
    app.add_handler(CallbackQueryHandler(on_svcother_custom, pattern="^svcother:custom$"))
    app.add_handler(CallbackQueryHandler(on_svcother_ff2017, pattern="^svcother:ff2017$"))

    # ---------- 🎁 Bonuslar (Xizmatlar ichida - Tekin almaz + Kunlik bonus) ----------
    app.add_handler(CallbackQueryHandler(on_quiz_button_callback, pattern="^svcbonus:quiz$"))
    app.add_handler(CallbackQueryHandler(on_account_bonus, pattern="^svcbonus:daily$"))

    # ---------- 👤 Profil (reply tugma + inline: Hisobim / Almaz yechish) ----------
    app.add_handler(MessageHandler(_exact(BTN_MAIN_PROFILE), on_profile_button))
    app.add_handler(CallbackQueryHandler(on_profile_account, pattern="^profile:account$"))
    app.add_handler(CallbackQueryHandler(on_withdraw_button_callback, pattern="^profile:withdraw$"))

    # ============================================================================
    # 🆕 Yangi asosiy menyu (6 tugma, 2 ustunda):
    # 💎 Almaz olish | 🛍 Xizmatlar
    # ⚙️ Nastroykalar | 🎉 Free Fire Niklar
    # 💰 To'lov usullari | 📬 Savollar (FAQ)
    # (📬 Savollar (FAQ) tugmasi matni eski BTN_FAQ bilan bir xil, shu sabab
    # yuqoridagi faq_conv avtomatik ishlaydi - qo'shimcha handler shart emas)
    # ============================================================================

    # ---------- 💎 Almaz olish ----------
    app.add_handler(MessageHandler(_exact(BTN_M2_DIAMONDS), on_m2_diamonds_button))
    app.add_handler(CallbackQueryHandler(on_diaget_free, pattern="^diaget:free$"))
    app.add_handler(CallbackQueryHandler(on_diaget_buy, pattern="^diaget:buy$"))

    # ---------- ⚙️ Nastroykalar ----------
    app.add_handler(MessageHandler(_exact(BTN_M2_SETTINGS), on_m2_settings_button))
    app.add_handler(CallbackQueryHandler(on_newset_back, pattern="^newset:back$"))
    app.add_handler(CallbackQueryHandler(on_newset_premium, pattern="^newset:premium$"))
    # Telefon/Planshet/PC nastroykalari - mavjud Free Fire menyusidagi funksiyalar
    # qayta ishlatiladi (kod takrorlanmasligi uchun)
    app.add_handler(CallbackQueryHandler(on_ff_phone, pattern="^newset:phone$"))
    app.add_handler(CallbackQueryHandler(on_ff_tablet, pattern="^newset:tablet$"))
    app.add_handler(CallbackQueryHandler(on_ff_pc, pattern="^newset:pc$"))

    # ---------- 🎉 Free Fire Niklar ----------
    app.add_handler(MessageHandler(_exact(BTN_M2_NICKS), on_m2_nicks_button))
    app.add_handler(CallbackQueryHandler(on_newnick_back, pattern="^newnick:back$"))
    app.add_handler(
        CallbackQueryHandler(
            on_newnick_category,
            pattern="^newnick:(gamer|super|pro|top|chiroyli)$",
        )
    )
    # "🛠 Nik Yasash" tugmasi mavjud "ffmenu:nick" conversation'ini ishga tushiradi
    # (yuqorida nick_conv allaqachon ro'yxatdan o'tgan)

    # ---------- 🛍 Xizmatlar ----------
    app.add_handler(MessageHandler(_exact(BTN_M2_SERVICES), on_m2_services_button))
    app.add_handler(CallbackQueryHandler(on_newsvc_back, pattern="^newsvc:back$"))
    app.add_handler(
        CallbackQueryHandler(
            on_newsvc_item,
            pattern="^newsvc:(ff2017|tournament|proxy|ffidm|cheat|news|music)$",
        )
    )

    # ---------- 💰 To'lov usullari ----------
    app.add_handler(MessageHandler(_exact(BTN_M2_PAYMENTS), on_m2_payments_button))
    app.add_handler(CallbackQueryHandler(on_pay_back, pattern="^pay:back$"))
    # "💎 Almaz yechish" - mavjud Profil bo'limidagi funksiya qayta ishlatiladi
    app.add_handler(CallbackQueryHandler(on_withdraw_button_callback, pattern="^pay:withdraw$"))
    app.add_handler(CallbackQueryHandler(on_pay_bonus_diamond, pattern="^pay:bonusdiamond$"))
    app.add_handler(CallbackQueryHandler(on_pay_daily_bonus, pattern="^pay:dailybonus$"))

    # ---------- 🎁 Sovg'alar (yangi bosh menyu tugmasi) ----------
    app.add_handler(MessageHandler(_exact(BTN_GIFTS), on_gifts_button))
    app.add_handler(CallbackQueryHandler(on_gift_free_diamond, pattern="^gift:free_diamond$"))
    app.add_handler(CallbackQueryHandler(on_gift_money_bonus, pattern="^gift:money_bonus$"))
    app.add_handler(CallbackQueryHandler(on_gift_diamond_bonus, pattern="^gift:diamond_bonus$"))

    # ---------- Statistika uchun umumiy loglash (barcha xabarlar) ----------
    app.add_handler(MessageHandler(filters.ALL, log_all_messages), group=1)

    return app


def main():
    app = build_application()
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
