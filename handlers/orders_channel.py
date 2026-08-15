# -*- coding: utf-8 -*-
"""📢 Bajarilgan buyurtmalar haqida @buyurtmalar_ff kanaliga avtomatik xabar.

Admin biror buyurtmani (Shaxsiy nastroyka, Maxsus rasm, Video, Musiqa va h.k.)
bajarib, tayyor natijani foydalanuvchiga yuborgach, shu yerdagi
`announce_order_completed` chaqiriladi va kanalga ketma-ket raqam bilan
("1# buyurtma bajarildi", "2# buyurtma bajarildi", ...) xabar tashlanadi.
"""

from telegram.error import TelegramError

import database as db
from config import ORDERS_CHANNEL_ID


async def announce_order_completed(bot, order_type_label: str, user, info: str = ""):
    """Kanalga avtomatik 'N# buyurtma bajarildi' xabarini yuboradi.

    - bot: context.bot
    - order_type_label: masalan "🆓 Bepul nastroyka", "💎 Maxsus rasm"
    - user: telegram.User (yoki shunga o'xshash first_name/username/id
      atributlariga ega obyekt)
    - info: buyurtma haqida qo'shimcha matn (model, tavsif, tarif va h.k.)
    """
    number = db.get_next_order_number()

    first_name = getattr(user, "first_name", None) or "-"
    username = getattr(user, "username", None)
    user_id = getattr(user, "id", None)

    text = (
        f"✅ <b>{number}# buyurtma bajarildi</b>\n\n"
        f"📦 Turi: {order_type_label}\n"
        f"👤 Foydalanuvchi: {first_name} (@{username or '—'})\n"
    )
    if user_id is not None:
        text += f"🆔 Telegram ID: <code>{user_id}</code>\n"
    if info:
        text += f"\n📝 Ma'lumot:\n{info}"

    try:
        await bot.send_message(chat_id=ORDERS_CHANNEL_ID, text=text, parse_mode="HTML")
    except TelegramError:
        pass
