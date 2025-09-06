# tgbot/handlers/application/postal_code.py
import re
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm
from keyboards.education import education_level_keyboard, EDUCATION_LEVELS

router = Router()

# Skip tugmasi
skip_postal_code_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⏭️ Pochta indeksini o'tkazib yuborish", callback_data="skip_postal_code")]
])

@router.message(ApplicationForm.postal_code, F.text)
async def get_postal_code(message: Message, state: FSMContext):
    postal_code = message.text.strip()

    # Faqat 5 yoki 6 xonali raqamga ruxsat
    if not re.fullmatch(r"\d{5,6}", postal_code):
        await message.answer("❌ Noto'g'ri format. Iltimos, 5 yoki 6 xonali raqam kiriting (masalan: 100000)")
        return

    # FSM ma'lumotiga yozib qo'yish
    await state.update_data(postal_code=postal_code)

    # Keyingi bosqich: ta'lim darajasi tugmalari
    await message.answer(
        "🎓 Iltimos, ma'lumotingizni tanlang:",
        reply_markup=education_level_keyboard
    )
    await state.set_state(ApplicationForm.education_level)

# Postal code ni o'tkazib yuborish
@router.callback_query(ApplicationForm.postal_code, F.data == "skip_postal_code")
async def skip_postal_code(callback: CallbackQuery, state: FSMContext):
    await state.update_data(postal_code="")  # serverga bo'sh boradi
    # Tugmani tozalaymiz va keyingi bosqichga o'tamiz
    await callback.message.edit_text("📬 Pochta indeksi o'tkazib yuborildi.")
    await callback.message.answer(
        "🎓 Iltimos, ma'lumotingizni tanlang:",
        reply_markup=education_level_keyboard
    )
    await state.set_state(ApplicationForm.education_level)
    await callback.answer()