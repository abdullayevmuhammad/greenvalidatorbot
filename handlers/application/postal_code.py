import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm
from keyboards.education_level import education_level_keyboard  # 👈 inline tugmalar import

router = Router()

@router.message(ApplicationForm.postal_code, F.text)
async def get_postal_code(message: Message, state: FSMContext):
    postal_code = message.text.strip()
    
    if not re.fullmatch(r"\d{5,6}", postal_code):
        await message.answer("❌ Noto'g'ri format. Iltimos, 5 yoki 6 xonali raqam kiriting (masalan: 100000)")
        return

    await state.update_data(postal_code=postal_code)
    
    # Inline tugmalar orqali ma'lumotni tanlash
    await message.answer(
        "🎓 Iltimos, ma'lumotingizni tanlang:",
        reply_markup=education_level_keyboard
    )
    await state.set_state(ApplicationForm.education_level)
