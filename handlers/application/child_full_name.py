from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm

router = Router()

@router.message(ApplicationForm.child_full_name, F.text)
async def handle_child_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    if not full_name:
        await message.answer("❌ Farzandning ismi bo‘sh bo‘lmasligi kerak.")
        return

    data = await state.get_data()
    current_child = data.get("current_child", 1)

    # ✅ Yangi farzand dict
    child = {
        "full_name": full_name,
        "status": "child"
    }

    # ✅ Eski ro‘yxatga qo‘shamiz
    dependents = data.get("dependents", [])
    dependents.append(child)
    await state.update_data(dependents=dependents)

    await message.answer(
        f"📄 Iltimos, {current_child}-farzandingizning tug‘ilganlik guvohnomasi yoki pasport faylini yuboring "
        f"(PDF, JPG yoki PNG, 2MB gacha):"
    )
    await state.set_state(ApplicationForm.child_passport)
