# tgbot/handlers/application/child_full_name.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm

router = Router()


# tgbot/handlers/application/child_full_name.py
@router.message(ApplicationForm.child_full_name, F.text)
async def handle_child_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    if not full_name:
        await message.answer("❌ Farzandning ismi bo'sh bo'lmasligi kerak.")
        return

    data = await state.get_data()
    current_child = data.get("current_child", 1)
    dependents = data.get("dependents", [])

    # Farzand ma'lumotlarini qo'shamiz
    dependents.append({
        "full_name": full_name,
        "status": "child",
        "photo_file": None,
        "passport_file": None
    })

    await state.update_data({
        "dependents": dependents,
        f"child_{current_child}_name": full_name
    })

    await message.answer(
        f"🖼 Iltimos, {current_child}-farzandingizning 600×600 formatdagi rasmini yuboring:"
    )
    await state.set_state(ApplicationForm.child_photo)