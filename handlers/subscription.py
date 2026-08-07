# -*- coding: utf-8 -*-
"""Majburiy obuna tekshiruvi uchun yordamchi funksiyalar."""

# -*- coding: utf-8 -*-
"""Majburiy obuna tekshiruvi uchun yordamchi funksiyalar."""

import asyncio
import time

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config import REQUIRED_CHANNELS

# Foydalanuvchi "to'liq obuna bo'lgan" deb tasdiqlangandan keyin, shu vaqt
# davomida (soniyalarda) qayta Telegram API'ga so'rov yubormay, keshdan
# foydalaniladi. Bu HAR BIR tugma bosilganda 5 ta kanalni ketma-ket
# tekshirish botni sekinlashtirmasligi uchun kerak.
_SUBSCRIPTION_CACHE_TTL = 300  # 5 daqiqa
_subscribed_until: dict[int, float] = {}


async def get_unsubscribed_channels(user_id: int, context: ContextTypes.DEFAULT_TYPE, use_cache: bool = True):
    """Foydalanuvchi obuna bo'lmagan kanallar ro'yxatini qaytaradi.

    Eslatma: bu funksiya ishlashi uchun bot har bir kanalda ADMIN
    bo'lishi shart, aks holda Telegram API a'zolik holatini bermaydi.

    Tezlik uchun: (1) agar foydalanuvchi yaqinda to'liq obuna bo'lgani
    tasdiqlangan bo'lsa - keshdan qaytariladi (API so'rovsiz); (2) barcha
    kanallar bir vaqtda (parallel) tekshiriladi, ketma-ket emas.
    """
    if use_cache:
        cached_until = _subscribed_until.get(user_id)
        if cached_until and cached_until > time.monotonic():
            return []

    results = await asyncio.gather(
        *(
            context.bot.get_chat_member(chat_id=f"@{ch['username']}", user_id=user_id)
            for ch in REQUIRED_CHANNELS
        ),
        return_exceptions=True,
    )

    unsubscribed = []
    for ch, res in zip(REQUIRED_CHANNELS, results):
        if isinstance(res, Exception):
            # Bot kanalda admin emas yoki kanal topilmadi - xavfsizlik uchun
            # foydalanuvchini obuna bo'lmagan deb hisoblaymiz.
            unsubscribed.append(ch)
        elif res.status in ("left", "kicked"):
            unsubscribed.append(ch)

    if not unsubscribed:
        _subscribed_until[user_id] = time.monotonic() + _SUBSCRIPTION_CACHE_TTL
    else:
        _subscribed_until.pop(user_id, None)

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
