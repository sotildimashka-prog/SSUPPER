# -*- coding: utf-8 -*-
"""Admin tomonidan tahrirlanadigan kontentni (matn yoki media bilan) yuborish uchun umumiy yordamchi."""

import database as db


async def send_stored_content(target, key: str, default_text: str, reply_markup=None, parse_mode="HTML"):
    """
    target - Message obyekti (update.message yoki query.message), unda
    reply_text/reply_photo/reply_video/reply_document metodlari bo'lishi kerak.
    key - app_settings ichidagi matn kaliti (masalan "cheat_text").
    Agar admin shu key uchun fayl/video/rasm biriktirgan bo'lsa, matn undan
    "caption" sifatida yuboriladi, aks holda oddiy matn xabari yuboriladi.
    """
    text = db.get_setting(key, default_text)
    media_raw = db.get_setting(f"{key}_media", "")

    if media_raw and "|" in media_raw:
        media_type, file_id = media_raw.split("|", 1)
        try:
            if media_type == "photo":
                await target.reply_photo(
                    file_id, caption=text, parse_mode=parse_mode, reply_markup=reply_markup
                )
                return
            if media_type == "video":
                await target.reply_video(
                    file_id, caption=text, parse_mode=parse_mode, reply_markup=reply_markup
                )
                return
            if media_type == "document":
                await target.reply_document(
                    file_id, caption=text, parse_mode=parse_mode, reply_markup=reply_markup
                )
                return
        except Exception:
            # Fayl allaqachon eskirgan yoki xato bo'lsa, matnga qaytamiz
            pass

    await target.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
