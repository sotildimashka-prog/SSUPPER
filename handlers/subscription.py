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
