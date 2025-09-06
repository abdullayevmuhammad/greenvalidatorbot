# tgbot/handlers/applcation/get_code_by_phone.py
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm
from utils.api import get_confirmation_by_phone

router = Router()


@router.message(ApplicationForm.phone)
async def handle_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(phone=phone)

    await message.answer("🔎 Ma'lumotlar tekshirilmoqda...")

    status, data = await get_confirmation_by_phone(phone)

    if status != 200 or not data:
        await message.answer("❌ Ushbu raqam bo‘yicha ariza topilmadi.")
        await state.clear()
        return

    applicants = data.get("applicants", [])
    if not applicants:
        await message.answer("📭 Ariza topilmadi.")
        await state.clear()
        return

    # Har bir applicant bo‘yicha natija chiqaramiz
    for app in applicants:
        fio = f"{app.get('first_name', '')} {app.get('last_name', '')}".strip()
        confirmation_file = app.get("confirmation_file")

        if confirmation_file:
            await message.answer(
                f"👤 {fio}\n📎 Confirmation fayl: {confirmation_file}"
            )
        else:
            await message.answer(
                f"👤 {fio}\n⌛️ Confirmation fayl hali joylanmagan."
            )

    await state.clear()
