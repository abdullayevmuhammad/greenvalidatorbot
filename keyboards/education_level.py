from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm
from keyboards.education import education_level_keyboard

router = Router()

# Boshlanishi: tugmalarni chiqarish
@router.message(ApplicationForm.email)
async def ask_education_level(message, state: FSMContext):
    await message.answer(
        "🎓 Ta'lim darajangizni tanlang:",
        reply_markup=education_level_keyboard
    )
    await state.set_state(ApplicationForm.education_level)

# Tugmani bosganda: callback handler
@router.callback_query(ApplicationForm.education_level)
async def get_education_level(callback: CallbackQuery, state: FSMContext):
    mapping = {
        "edu_oliy": "Oliy",
        "edu_orta_maxsus": "O‘rta maxsus",
        "edu_orta": "O‘rta",
        "edu_boshlangich": "Boshlang‘ich"
    }

    data = callback.data
    if data not in mapping:
        await callback.answer("❌ Noto‘g‘ri tanlov", show_alert=True)
        return

    await state.update_data(education_level=mapping[data])
    await callback.message.delete_reply_markup()
    await callback.message.answer("📮 Endi yashash manzilingizni kiriting:")
    await state.set_state(ApplicationForm.address)
    await callback.answer()
