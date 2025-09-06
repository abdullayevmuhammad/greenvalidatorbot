# tgbot/handlers/application/addres.py
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm

router = Router()

# Skip tugmasi
skip_postal_code_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⏭️ Pochta indeksini o'tkazib yuborish", callback_data="skip_postal_code")]
])


@router.message(ApplicationForm.address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)

    # Pochta indeksi haqida tushuntirish bilan
    explanation = (
        "📬 Iltimos, pochta indeksingizni kiriting:\n\n"
        "• Pochta indeksi - siz yashaydigan hududning raqamli identifikatori\n"
        "• Agar aniq bilmasangiz, quyidagi manbalardan topishingiz mumkin:\n"
        "  https://www.goldenpages.uz/uz/pochta/\n"
        "Indeksni shu ko'rinishda kiriting: 100001\n\n"
        "Xohlamasangiz, quyidagi tugma orqali o'tkazib yuborishingiz mumkin."
    )

    await message.answer(explanation, reply_markup=skip_postal_code_kb)
    await state.set_state(ApplicationForm.postal_code)