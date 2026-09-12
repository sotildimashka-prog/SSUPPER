# -*- coding: utf-8 -*-
"""⚙️ Nastroykalar bo'limi - brend va model tanlash callback'lari.

Har bir model uchun kontent admin panel orqali qo'shiladi va
database.get_nastroyka_content orqali o'qiladi (matn / rasm / video,
izoh bilan yoki izohsiz)."""

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import database as db
from keyboards import brands_keyboard, models_keyboard, model_back_keyboard
from data.settings_data import PHONES

SETTINGS_INTRO_TEXT = (
    "📱 <b>TELEFON MODELINGIZNI TANLANG!</b>\n\n"
    "✨ Qurilmangizga mos Free Fire nastroykasini tanlang va qulay "
    "sozlamalardan foydalaning.\n\n"
    "Telefon brendini tanlang 👇"
)

NOT_ADDED_TEXT = (
    "⚠️ Ushbu model uchun hozircha nastroyka mavjud emas.\n"
    "👑 Admin tez orada yangi nastroyka qo'shadi."
)


def _find_brand(model_name: str) -> str | None:
    for brand, models in PHONES.items():
        if model_name in models:
            return brand
    return None


async def on_brand_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    brand = query.data.split(":", 1)[1]
    if brand not in PHONES:
        return
    await query.edit_message_text(
        f"{brand}\n\nModelni tanlang 👇",
        reply_markup=models_keyboard(brand),
    )


async def on_back_to_brands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        SETTINGS_INTRO_TEXT,
        parse_mode="HTML",
        reply_markup=brands_keyboard(),
    )


async def on_model_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    model_name = query.data.split(":", 1)[1]

    brand = _find_brand(model_name)
    markup = model_back_keyboard(brand) if brand else None
    content = db.get_nastroyka_content(model_name)

    if not content:
        try:
            await query.edit_message_text(
                f"📱 <b>{model_name}</b>\n\n{NOT_ADDED_TEXT}",
                parse_mode="HTML",
                reply_markup=markup,
            )
        except TelegramError:
            pass
        return

    ctype = content.get("type", "text")
    file_id = content.get("file_id", "")
    caption = content.get("caption", "")
    text = content.get("text", "")
    header = f"📱 <b>{model_name}</b>\n\n"

    if ctype == "text" or not file_id:
        body = text or caption or NOT_ADDED_TEXT
        try:
            await query.edit_message_text(
                header + body, parse_mode="HTML", reply_markup=markup
            )
        except TelegramError:
            pass
        return

    # Rasm/video kontent: matnli xabarni media xabariga "edit" qilib
    # bo'lmaydi, shuning uchun eski xabarni o'chirib, yangi media
    # xabar yuboramiz.
    try:
        await query.message.delete()
    except TelegramError:
        pass

    full_caption = (header + caption) if caption else header + f"<b>{model_name}</b>"
    chat_id = query.message.chat_id
    if ctype == "photo":
        await context.bot.send_photo(
            chat_id, file_id, caption=full_caption, parse_mode="HTML", reply_markup=markup
        )
    elif ctype == "video":
        await context.bot.send_video(
            chat_id, file_id, caption=full_caption, parse_mode="HTML", reply_markup=markup
        )
