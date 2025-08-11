# handlers/applications/email.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import re

from states.application import ApplicationForm

router = Router()

# ✅ Emailni matn sifatida qabul qilish (ixtiyoriy, lekin yozsa tekshiramiz)
@router.message(ApplicationForm.email, F.text)
async def handle_email(message: Message, state: FSMContext):
    email = message.text.strip()

    # Email kiritilgan bo‘lsa — formatini tekshiramiz
    if email and not re.fullmatch(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
        await message.answer("❌ Email noto'g'ri ko'rinmoqda. Iltimos, haqiqiy email manzil kiriting (masalan: example@gmail.com).")
        return

    # Bo‘sh bo‘lsa ham saqlaymiz (ixtiyoriy)
    await state.update_data(email=email)

    await message.answer(
        "🏠 Iltimos, to'liq manzilingizni kiriting:\n"
        "(Shahar/tuman, ko'cha, uy raqami, kvartira)\n"
        "Masalan: Toshkent shahar, Mirzo Ulug'bek ko'chasi, 45-uy, 12-xonadon"
    )
    await state.set_state(ApplicationForm.address)

# ✅ Inline tugma: emailni o‘tkazib yuborish
@router.callback_query(ApplicationForm.email, F.data == "skip_email")
async def skip_email(callback: CallbackQuery, state: FSMContext):
    await state.update_data(email="")  # serverga bo‘sh boradi
    # Tugmani tozalaymiz va keyingi bosqichga o‘tamiz
    await callback.message.edit_text("📧 Email o‘tkazib yuborildi.")
    await callback.message.answer(
        "🏠 Iltimos, to'liq manzilingizni kiriting:\n"
        "(Shahar/tuman, ko'cha, uy raqami, kvartira)\n"
        "Masalan: Toshkent shahar, Mirzo Ulug'bek ko'chasi, 45-uy, 12-xonadon"
    )
    await state.set_state(ApplicationForm.address)
    await callback.answer()
