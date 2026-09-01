# -*- coding: utf-8 -*-
"""Callback-query xabarlarini xavfsiz tahrirlash uchun umumiy yordamchi.

XATOLIK SABABI:
Ba'zi navigatsiya zanjirlari (masalan "🛠️ Barcha xizmatlar" ro'yxati yoki
/start banneri) asl xabarni RASM (caption bilan) sifatida yuboradi va uni
inline tugmalar orqali TAHRIRLAB boradi. Bu holatda menyu ichidagi handlerlar
to'g'ridan-to'g'ri `query.edit_message_text(...)` chaqirsa, Telegram

    telegram.error.BadRequest: There is no text in the message to edit

xatosini qaytaradi - chunki rasm xabarida "text" emas, "caption" bo'ladi.
Aynan shu sabab loglarda handlers/ffmenu.py, handlers/newflow.py va
handlers/games.py dagi bir qancha funksiyalarda takroriy xatolikka olib
kelgan edi.

YECHIM:
`safe_edit_message` xabar turini (rasm/matn) avtomatik aniqlaydi va mos
usulni qo'llaydi:
  - xabar rasm (caption) bo'lsa -> edit_message_caption
  - aks holda                   -> edit_message_text
Agar ikkalasi ham chiqmasa (masalan xabar juda eski yoki o'chirilgan bo'lsa),
bot to'xtab qolmasligi uchun foydalanuvchiga YANGI xabar yuboriladi.

Ishlatilishi avvalgi `query.edit_message_text(...)` chaqiruvi bilan bir xil -
faqat oldiga `query` argumenti qo'shiladi:

    await query.edit_message_text(text, reply_markup=kb, parse_mode="HTML")
    # =>
    await safe_edit_message(query, text, reply_markup=kb, parse_mode="HTML")
"""

from telegram.error import TelegramError


async def safe_edit_message(query, *args, **kwargs):
    msg = query.message

    # edit_message_text bilan bir xil chaqiruvni (positional yoki text=)
    # caption chaqiruviga moslashtiramiz.
    caption_args = args
    caption_kwargs = dict(kwargs)
    if msg is not None and msg.photo:
        if caption_args:
            caption_kwargs.setdefault("caption", caption_args[0])
            caption_args = caption_args[1:]
        elif "text" in caption_kwargs:
            caption_kwargs["caption"] = caption_kwargs.pop("text")
        caption_kwargs.pop("disable_web_page_preview", None)

    try:
        if msg is not None and msg.photo:
            return await query.edit_message_caption(*caption_args, **caption_kwargs)
        return await query.edit_message_text(*args, **kwargs)
    except TelegramError:
        text_val = (
            kwargs.get("text")
            or kwargs.get("caption")
            or (args[0] if args else "")
        )
        reply_markup = kwargs.get("reply_markup")
        parse_mode = kwargs.get("parse_mode")
        chat_id = None
        if query.from_user is not None:
            chat_id = query.from_user.id
        elif msg is not None:
            chat_id = msg.chat.id

        if chat_id is None:
            # Yuboradigan joy yo'q - jim tugatamiz, bot yiqilmasligi kerak.
            return None

        return await query.get_bot().send_message(
            chat_id=chat_id,
            text=text_val,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )
