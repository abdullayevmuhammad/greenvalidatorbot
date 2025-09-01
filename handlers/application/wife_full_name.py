# handlers/application/wife_full_name.py
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm

router = Router()

@router.message(ApplicationForm.wife_full_name)
async def handle_wife_full_name(message: Message, state: FSMContext):
    wife_name = message.text.strip()
    if not wife_name:
        await message.answer("❌ Iltimos, to'liq ismni kiriting.")
        return

    # dependents ro'yxatini yangilash
    data = await state.get_data()
    dependents = data.get("dependents", [])

    # agar wife hali qo'shilmagan bo'lsa, qo'shamiz
    wife_dep = next((d for d in dependents if d.get("status") == "wife"), None)
    if not wife_dep:
        dependents.append({
            "full_name": wife_name,
            "status": "wife",
            "passport_file": None,
            "photo_file": None
        })
    else:
        wife_dep["full_name"] = wife_name

    await state.update_data(dependents=dependents)

    await message.answer(
        "📄 Turmush o'rtog'ingizning pasport faylini yuboring (JPG, PNG yoki PDF, 2MB gacha):"
    )
    await state.set_state(ApplicationForm.wife_passport)
