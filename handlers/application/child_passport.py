# tgbot/handlers/application/child_passport.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.file import get_download_path, safe_filename
from utils.validators import validate_file_extension, validate_file_size
from states.application import ApplicationForm
from .confirm import ask_confirmation

router = Router()

# tgbot/handlers/application/child_passport.py
@router.message(ApplicationForm.child_passport, F.document)
async def handle_child_passport(message: Message, state: FSMContext):
    file = message.document
    safe_name = safe_filename(file.file_id, file.file_name, max_length=100)
    file_path = get_download_path(safe_name)

    try:
        await message.bot.download(file, destination=file_path)
        validate_file_extension(safe_name)
        validate_file_size(file.file_size)
    except Exception:
        await message.answer("❌ Fayl noto'g'ri. Faqat PDF, JPG, PNG (2MB gacha) yuboring.")
        return

    data = await state.get_data()
    current_child = data.get("current_child", 1)
    children_total = data.get("children_count", 0)
    dependents = data.get("dependents", [])

    # Oxirgi qo'shilgan farzandni topamiz (current_child indeksiga asosan)
    child_index = None
    child_count = 0
    for i, dep in enumerate(dependents):
        if dep.get("status") == "child":
            child_count += 1
            if child_count == current_child:
                child_index = i
                break

    if child_index is not None:
        # Farzand ma'lumotlarini yangilaymiz
        dependents[child_index]["passport_file"] = file_path
    else:
        # Yangi farzand qo'shamiz
        dependents.append({
            "full_name": data.get(f"child_{current_child}_name", f"Farzand {current_child}"),
            "status": "child",
            "photo_file": data.get(f"child_{current_child}_photo"),
            "passport_file": file_path
        })

    await state.update_data({
        "dependents": dependents,
        f"child_{current_child}_passport": file_path
    })

    # Keyingi farzand yoki tasdiqlash
    if current_child < children_total:
        await state.update_data({"current_child": current_child + 1})
        await message.answer(f"👶 {current_child + 1}-farzandingizning to'liq ismini kiriting:")
        await state.set_state(ApplicationForm.child_full_name)
    else:
        await ask_confirmation(message, state)