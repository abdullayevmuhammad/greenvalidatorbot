import re
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm

router = Router()
skip_email_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⏭️ Emailni o‘tkazib yuborish", callback_data="skip_email")]
])
# Telefon raqamni qabul qilish
@router.message(ApplicationForm.phone_number, F.text)
async def handle_phone_number(message: Message, state: FSMContext):
    phone = message.text.strip()

    # Regex bilan tekshirish: +998XXXXXXXXX
    if not re.fullmatch(r"^\+998\d{9}$", phone):
        await message.answer("❌ Telefon raqam noto‘g‘ri. Iltimos, +998 bilan boshlanuvchi 13 xonali raqam yuboring (masalan: +998901234567).")
        return

    await state.update_data(phone_number=phone)
    await message.answer(
        "📧 Endi email manzilingizni yuboring (masalan: example@gmail.com):\n"
        "Agar xohlamasangiz, quyidagi tugma orqali o‘tkazib yuborishingiz mumkin.",
        reply_markup=skip_email_kb
    )
    await state.set_state(ApplicationForm.email)