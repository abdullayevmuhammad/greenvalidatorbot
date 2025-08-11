from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm

router = Router()

@router.message(ApplicationForm.address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    
    # Pochta indeksi haqida tushuntirish bilan
    explanation = (
        "📬 Iltimos, pochta indeksingizni kiriting:\n\n"
        "• Pochta indeksi - siz yashaydigan hududning raqamli identifikatori\n"
        "• Masalan: Toshkent shahri uchun 100000\n"
        "• Agar aniq bilmasangiz, quyidagi manbalardan topishingiz mumkin:\n"
        "  - https://pochta.uz/uz/services/postal-codes\n"
        "  - Mahallangizdagi pochta bo'limida so'rash\n"
        "  - Mahalla raisligida ma'lumot olish\n\n"
        "Indeksni shu ko'rinishda kiriting: 100001"
    )
    
    await message.answer(explanation)
    await state.set_state(ApplicationForm.postal_code)