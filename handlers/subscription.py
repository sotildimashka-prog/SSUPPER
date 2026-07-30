# -*- coding: utf-8 -*-
"""Majburiy obuna tekshiruvi uchun yordamchi funksiyalar."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config import REQUIRED_CHANNELS


async def get_unsubscribed_channels(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi obuna bo'lmagan kanallar ro'yxatini qaytaradi.

    Eslatma: bu funksiya ishlashi uchun bot har bir kanalda ADMIN
    bo'lishi shart, aks holda Telegram API a'zolik holatini bermaydi.
    """
    unsubscribed = []
    for ch in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(
                chat_id=f"@{ch['username']}", user_id=user_id
            )
            if member.status in ("left", "kicked"):
                unsubscribed.append(ch)
        except TelegramError:
            # Bot kanalda admin emas yoki kanal topilmadi - xavfsizlik uchun
            # foydalanuvchini obuna bo'lmagan deb hisoblaymiz.
            unsubscribed.append(ch)
    return unsubscribed


async def require_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Yangi bo'limlar (Rasm/Video Yasash) ochilishidan oldin majburiy obunani
    tekshiradi. Agar foydalanuvchi obuna bo'lmagan bo'lsa - kanallarga
    qo'shilish tugmalari va "✅ Tekshirish" tugmasini yuboradi va False
    qaytaradi (chaqiruvchi handler shu holatda davom etmasligi kerak)."""
    import database as db
    from keyboards import subscription_keyboard

    user = update.effective_user
    unsubscribed = await get_unsubscribed_channels(user.id, context)
    if not unsubscribed:
        return True

    lang = db.get_user_language(user.id) or "uz"
    if lang == "ru":
        text = (
            "📢 <b>Чтобы пользоваться этим разделом, сначала подпишитесь на каналы ниже!</b>\n\n"
            "После подписки на все каналы нажмите кнопку <b>✅ Я подписался</b> внизу 👇"
        )
    else:
        text = (
            "📢 <b>Bu bo'limdan foydalanish uchun avval quyidagi kanallarga obuna bo'ling!</b>\n\n"
            "Barcha kanallarga obuna bo'lgach, pastdagi <b>✅ Obuna bo'ldim</b> "
            "tugmasini bosing 👇"
        )

    target = update.effective_message
    await target.reply_text(text, parse_mode="HTML", reply_markup=subscription_keyboard())
    return False
