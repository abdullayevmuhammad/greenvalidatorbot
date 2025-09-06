# tgbot/handlers/applcation/phone.py
import re
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm

router = Router()

PHONE_RE = re.compile(r'^\+998\d{9}$')

skip_email_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⏭️ Emailni o'tkazib yuborish", callback_data="skip_email")]
])

@router.message(ApplicationForm.phone_number, F.text)
async def handle_phone_number(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    # ixtiyoriy: bo'sh joy/tire/qavslarni olib tashlab normalizatsiya qilamiz
    phone = re.sub(r'[^\d+]', '', raw)

    # ✅ Regex: +998XXXXXXXXX
    if not PHONE_RE.fullmatch(phone):
        await message.answer(
            "❌ Telefon raqam noto'g'ri.\n"
            "Iltimos, <code>+998XXXXXXXXX</code> ko'rinishida yuboring (masalan: <code>+998901234567</code>).",
            parse_mode="HTML"
        )
        return

    # ✅ Faqat formatni tekshiramiz, serverda mavjudligini tekshirmaymiz
    await state.update_data(phone_number=phone)
    await message.answer(
        "📧 Endi email manzilingizni yuboring (masalan: <code>example@gmail.com</code>):\n"
        "Xohlamasangiz, quyidagi tugma orqali o'tkazib yuborishingiz mumkin.",
        reply_markup=skip_email_kb,
        parse_mode="HTML"
    )
    await state.set_state(ApplicationForm.email)