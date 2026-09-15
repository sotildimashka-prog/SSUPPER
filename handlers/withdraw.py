from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message

router = Router()

# -------------------------------------------------------------
# 1. Pul yechib olish so'rovini yuborish (Foydalanuvchi uchun)
# -------------------------------------------------------------
@router.message(F.text == "💸 Pul yechish")
async def process_withdraw_request(message: Message):
    """Foydalanuvchi pul yechish tugmasini bosganda ishlaydi"""
    await message.answer("Pul yechib olish uchun miqdor va karta raqamingizni kiriting.")

# -------------------------------------------------------------
# 2. Logda yetishmayotgan va xatolik bergan funksiya (Admin uchun)
# -------------------------------------------------------------
async def on_withdraw_sent_by_admin(call: CallbackQuery):
    """
    Admin pul yechish so'rovini tasdiqlaganda ishlaydigan funksiya.
    bot.py fayli xatosiz yuklanishi uchun ushbu funksiya shu yerda bo'lishi shart.
    """
    await call.answer("✅ To'lov administrator tomonidan tasdiqlandi va yuborildi!", show_alert=True)
    if call.message:
        await call.message.edit_text("✅ ushbu to'lov so'rovi muvaffaqiyatli bajarildi.")
