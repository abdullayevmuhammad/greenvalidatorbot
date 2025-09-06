# handlers/application/wife_full_name.py
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm

router = Router()

# handlers/application/wife_full_name.py
@router.message(ApplicationForm.wife_full_name)
async def handle_wife_full_name(message: Message, state: FSMContext):
    wife_name = message.text.strip()
    if not wife_name:
        await message.answer("❌ Iltimos, to'liq ismni kiriting.")
        return

    # Avvalgi dependents ro'yxatini olish
    data = await state.get_data()
    dependents = data.get("dependents", [])

    # Xotin ma'lumotlarini yangilash yoki qo'shish
    wife_index = None
    for i, dep in enumerate(dependents):
        if dep.get("status") == "wife":
            wife_index = i
            break

    if wife_index is not None:
        # Xotin allaqachon mavjud, yangilaymiz
        dependents[wife_index]["full_name"] = wife_name
    else:
        # Yangi xotin qo'shamiz
        dependents.append({
            "full_name": wife_name,
            "status": "wife",
            "passport_file": None,
            "photo_file": None
        })

    await state.update_data(
        wife_full_name=wife_name,
        dependents=dependents
    )

    await message.answer(
        "📄 Turmush o'rtog'ingizning pasport faylini yuboring (JPG, PNG yoki PDF, 2MB gacha):"
    )
    await state.set_state(ApplicationForm.wife_passport)