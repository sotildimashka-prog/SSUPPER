# -*- coding: utf-8 -*-
"""🆕 Yangi asosiy menyu (2 ustunli, 6 tugmali) bo'limlari:

💎 Almaz olish | 🛍 Xizmatlar
⚙️ Nastroykalar | 🎉 Free Fire Niklar
💰 To'lov usullari | 📬 Savollar (FAQ)

Bu modul faqat YANGI bo'limlarning kirish nuqtalarini o'z ichiga oladi -
eski funksiyalar (handlers/diamonds.py, handlers/withdraw.py, handlers/quiz.py,
handlers/custom.py, handlers/ffmenu.py va h.k.) o'zgarishsiz qoladi va
qayta ishlatiladi.
"""

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from keyboards import (
    diamonds_get_keyboard,
    diamonds_entry_keyboard,
    new_settings_menu_keyboard,
    new_settings_back_keyboard,
    new_nicks_menu_keyboard,
    new_nicks_back_keyboard,
    new_services_menu_keyboard,
    service_channel_keyboard,
    newsvc_portal_keyboard,
    payments_menu_keyboard,
    payments_back_keyboard,
    custom_entry_keyboard,
)
from data.nicknames_data import (
    GAMER_NICKNAMES,
    SUPER_NICKNAMES,
    PRO_NICKNAMES,
    TOP_NICKNAMES,
    CHIROYLI_NICKNAMES,
)

# ============================================================================
# 💎 Almaz olish
# ============================================================================

async def on_m2_diamonds_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 <b>Almaz olish</b>\n\n"
        "Almazni qanday olmoqchisiz? 👇",
        parse_mode="HTML",
        reply_markup=diamonds_get_keyboard(),
    )


async def on_diaget_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🆓 Tekin Almaz - mavjud 'Savol-javob' (Tekin almaz) oqimi qayta ishlatiladi."""
    from handlers.quiz import on_quiz_button_callback

    await on_quiz_button_callback(update, context)


async def on_diaget_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💎 Almaz sotib olish - mavjud xarid oqimi (Admin/Bot orqali) qayta ishlatiladi."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💎 <b>Almaz sotib olish</b>\n\nQanday yo'l bilan sotib olmoqchisiz?",
        parse_mode="HTML",
        reply_markup=diamonds_entry_keyboard(),
    )


# ============================================================================
# ⚙️ Nastroykalar
# ============================================================================

NASTROYKALAR_TEXT = "⚙️ <b>Nastroykalar</b>\n\nKerakli bo'limni tanlang 👇"

PREMIUM_TEXT = (
    "🎁✨ <b>MAXSUS NASTROYKALAR</b> ✨🎁\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    "💎 Premium o'yinchilar uchun maxsus tayyorlangan VIP nastroykalar!\n\n"
    "🔥 Yuqori aniqlik (sensitivity)\n"
    "🎯 Maksimal headshot foizi\n"
    "⚡️ Tezkor va silliq gameplay\n"
    "👑 Faqat VIP mijozlar uchun\n\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "Quyidagi variantlardan birini tanlang 👇"
)


async def on_m2_settings_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        NASTROYKALAR_TEXT, parse_mode="HTML", reply_markup=new_settings_menu_keyboard()
    )


async def on_newset_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        NASTROYKALAR_TEXT, parse_mode="HTML", reply_markup=new_settings_menu_keyboard()
    )


async def on_newset_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        PREMIUM_TEXT, parse_mode="HTML", reply_markup=custom_entry_keyboard()
    )


# ============================================================================
# 🎉 Free Fire Niklar
# ============================================================================

NICKS_MENU_TEXT = "🎉 <b>Free Fire Niklar</b>\n\nKategoriyani tanlang 👇"

NICK_CATEGORIES = {
    "gamer": ("🎮 Gamer Niklar", GAMER_NICKNAMES),
    "super": ("👑 Super Niklar", SUPER_NICKNAMES),
    "pro": ("🔥 Pro Niklar", PRO_NICKNAMES),
    "top": ("⚡ Top Niklar", TOP_NICKNAMES),
    "chiroyli": ("✨ Chiroyli Niklar", CHIROYLI_NICKNAMES),
}


async def on_m2_nicks_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        NICKS_MENU_TEXT, parse_mode="HTML", reply_markup=new_nicks_menu_keyboard()
    )


async def on_newnick_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        NICKS_MENU_TEXT, parse_mode="HTML", reply_markup=new_nicks_menu_keyboard()
    )


async def on_newnick_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.split(":", 1)[1]
    title, nicks = NICK_CATEGORIES.get(category, (None, None))
    if not nicks:
        return

    lines = [f"<code>{n}</code>" for n in nicks]
    text = f"{title}\n\n" + "\n".join(lines) + "\n\n👆 Ustiga bosib nusxa olishingiz mumkin."
    await query.edit_message_text(
        text, parse_mode="HTML", reply_markup=new_nicks_back_keyboard()
    )


# ============================================================================
# 🛍 Xizmatlar
# ============================================================================

SERVICES_MENU_TEXT = "🛍 <b>Xizmatlar</b>\n\nKerakli xizmatni tanlang 👇"

SERVICE_TITLES = {
    "ff2017": "🎮 Free Fire 2017",
    "tournament": "🏆 Free Fire Turnirlari",
    "proxy": "🌐 Proxy Server",
    "ffidm": "🆔 FF IDM",
    "cheat": "💀 Cheat Panel",
    "news": "📰 Free Fire Yangiliklari",
    "music": "🎵 Free Fire Qo'shiqlari",
}

SERVICE_CHANNEL_TEXT = (
    "📢 Ushbu xizmat faqat rasmiy Telegram kanalimiz orqali taqdim etiladi. "
    "Batafsil ma'lumot olish uchun quyidagi tugma orqali kanalga qo'shiling."
)


async def on_m2_services_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        SERVICES_MENU_TEXT, parse_mode="HTML", reply_markup=new_services_menu_keyboard()
    )


async def on_newsvc_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        SERVICES_MENU_TEXT, parse_mode="HTML", reply_markup=new_services_menu_keyboard()
    )


async def on_newsvc_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    title = SERVICE_TITLES.get(key, "🛍 Xizmat")

    # 🏆 Turnirlar va 📰 Yangiliklar - Free Fire Portal saytiga (Web App) yo'naltiriladi
    if key in ("tournament", "news"):
        text = (
            f"{title}\n\n"
            "🗺 Barcha Free Fire yangiliklari va turnirlar Free Fire Portal "
            "saytida joylashgan. Pastdagi tugma orqali Telegram ichida ochiladi 👇"
        )
        await query.edit_message_text(
            text, parse_mode="HTML", reply_markup=newsvc_portal_keyboard()
        )
        return

    text = f"{title}\n\n{SERVICE_CHANNEL_TEXT}"
    await query.edit_message_text(
        text, parse_mode="HTML", reply_markup=service_channel_keyboard()
    )


# ============================================================================
# 💰 To'lov usullari
# ============================================================================

PAYMENTS_MENU_TEXT = "💰 <b>To'lov usullari</b>\n\nKerakli bo'limni tanlang 👇"


async def on_m2_payments_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        PAYMENTS_MENU_TEXT, parse_mode="HTML", reply_markup=payments_menu_keyboard()
    )


async def on_pay_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        PAYMENTS_MENU_TEXT, parse_mode="HTML", reply_markup=payments_menu_keyboard()
    )


async def on_pay_bonus_diamond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🌙 Bonus Almaz - foydalanuvchi har kuni (kalendar kuni bo'yicha) bonus olishi mumkin."""
    query = update.callback_query
    user_id = query.from_user.id

    given = db.claim_diamond_bonus(user_id)
    total = db.get_quiz_diamonds(user_id)

    if given:
        await query.answer(
            f"🎉 Sizga {db.DIAMOND_BONUS_AMOUNT} 💎 bonus almaz berildi!", show_alert=True
        )
        await query.edit_message_text(
            "🌙 <b>Bonus Almaz olindi!</b>\n\n"
            f"💎 +{db.DIAMOND_BONUS_AMOUNT} almaz hisobingizga qo'shildi.\n"
            f"💎 Jami almazlaringiz: <b>{total}</b>\n\n"
            "Ertaga qaytadan olishingiz mumkin!",
            parse_mode="HTML",
            reply_markup=payments_back_keyboard(),
        )
    else:
        await query.answer(
            "🌙 Siz bugungi Bonus Almazni allaqachon oldingiz. Ertaga qaytadan urinib ko'ring!",
            show_alert=True,
        )
        await query.edit_message_text(
            "🌙 <b>Bonus Almaz</b>\n\n"
            "✅ Siz bugungi bonusingizni allaqachon olib bo'ldingiz.\n"
            f"💎 Jami almazlaringiz: <b>{total}</b>\n\n"
            "🕛 Ertaga qaytadan urinib ko'ring!",
            parse_mode="HTML",
            reply_markup=payments_back_keyboard(),
        )


def _format_hms(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours} soat {minutes} daqiqa"


async def on_pay_daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💵 Kunlik Bonus - har 24 soatda avtomatik ravishda 20 so'm balansga qo'shiladi."""
    query = update.callback_query
    user_id = query.from_user.id

    given, info = db.try_give_daily_money_bonus(user_id)
    balance = db.get_balance(user_id)

    if given:
        await query.answer(
            f"🎉 Sizga avtomatik ravishda {db.DAILY_MONEY_BONUS_AMOUNT} so'm bonus berildi!",
            show_alert=True,
        )
        await query.edit_message_text(
            "💵 <b>Kunlik Bonus berildi!</b>\n\n"
            f"✅ +{db.DAILY_MONEY_BONUS_AMOUNT} so'm avtomatik ravishda hisobingizga qo'shildi.\n"
            f"💰 Joriy balans: <b>{balance:,} so'm</b>\n\n".replace(",", ".")
            + "🕛 Keyingi bonus 24 soatdan so'ng avtomatik qo'shiladi.",
            parse_mode="HTML",
            reply_markup=payments_back_keyboard(),
        )
    else:
        await query.answer("🕛 Kunlik bonus hali tayyor emas.", show_alert=True)
        await query.edit_message_text(
            "💵 <b>Kunlik Bonus</b>\n\n"
            f"🕛 Har 24 soatda avtomatik ravishda {db.DAILY_MONEY_BONUS_AMOUNT} so'm beriladi.\n"
            f"⏳ Keyingi bonusgacha: <b>{_format_hms(info)}</b>\n"
            f"💰 Joriy balans: <b>{balance:,} so'm</b>".replace(",", "."),
            parse_mode="HTML",
            reply_markup=payments_back_keyboard(),
        )
