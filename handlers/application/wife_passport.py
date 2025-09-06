# tgbot/handlers/applcation/wife_passport.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.file import get_download_path, safe_filename
from utils.validators import validate_file_extension, validate_file_size
from states.application import ApplicationForm

router = Router()

# tgbot/handlers/application/wife_passport.py
@router.message(ApplicationForm.wife_passport, F.document)
async def handle_wife_passport(message: Message, state: FSMContext):
    file = message.document
    safe_name = safe_filename(file.file_id, file.file_name, max_length=100)
    file_path = get_download_path(safe_name)

    try:
        await message.bot.download(file, destination=file_path)
        validate_file_extension(safe_name)
        validate_file_size(file.file_size)
    except Exception:
        await message.answer(
            "❌ Fayl noto‘g‘ri. Faqat PDF, JPG, PNG (2MB gacha) yuboring."
        )
        return

    data = await state.get_data()
    dependents = data.get("dependents", [])
    wife_name = data.get("wife_full_name", "Turmush o'rtog'i")

    # Xotin ma'lumotlarini yangilash
    wife_index = None
    for i, dep in enumerate(dependents):
        if dep.get("status") == "wife":
            wife_index = i
            break

    if wife_index is not None:
        # Xotin allaqachon mavjud, yangilaymiz
        dependents[wife_index]["passport_file"] = file_path
    else:
        # Yangi xotin qo'shamiz
        dependents.append({
            "full_name": wife_name,
            "status": "wife",
            "passport_file": file_path,
            "photo_file": None
        })

    await state.update_data(
        wife_passport_file=file_path,
        dependents=dependents
    )

    await message.answer(
        "📸 Turmush o'rtog'ingizning 600x600 hajmdagi fotosuratini yuboring (JPG, PNG, 2MB gacha):"
    )
    await state.set_state(ApplicationForm.wife_photo)