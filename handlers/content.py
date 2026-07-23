# -*- coding: utf-8 -*-
"""Admin tomonidan tahrirlanadigan matnlarni (app_settings) yuborish uchun umumiy yordamchi."""

import database as db


async def send_stored_content(message, setting_key: str, default_text: str, reply_markup=None):
    text = db.get_setting(setting_key, default_text)
    await message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
