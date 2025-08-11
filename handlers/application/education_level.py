from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm
from keyboards.education import education_level_keyboard
from keyboards.marital_status import marital_status_keyboard

router = Router()

# Emaildan keyin chiqadigan tugmalar
@router.message(ApplicationForm.email)
async def ask_education_level(message: Message, state: FSMContext):
    await message.answer(
        "🎓 Ta'lim darajangizni tanlang:",
        reply_markup=education_level_keyboard
    )
    await state.set_state(ApplicationForm.education_level)

# Tugma bosilganda javob
@router.callback_query(ApplicationForm.education_level)
async def get_education_level(callback: CallbackQuery, state: FSMContext):
    mapping = {
        "edu_oliy": "Oliy",
        "edu_orta_maxsus": "O‘rta maxsus",
        "edu_umumiy_orta": "Umumiy o‘rta",
        "edu_boshlangich": "Boshlang‘ich"
    }

    data = callback.data
    if data not in mapping:
        await callback.answer("❌ Noto‘g‘ri tanlov", show_alert=True)
        return

    await state.update_data(education_level=mapping[data])
    await callback.message.delete_reply_markup()

    # Oilaviy holat tugmalarini chiqarish
    await callback.message.answer(
        "💍 Oilaviy holatingizni tanlang:",
        reply_markup=marital_status_keyboard
    )
    await state.set_state(ApplicationForm.marital_status)
    await callback.answer()
