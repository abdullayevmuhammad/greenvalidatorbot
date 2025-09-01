from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.file import get_download_path, safe_filename
from utils.validators import validate_file_extension, validate_file_size
from states.application import ApplicationForm

router = Router()

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

    # dependents ro'yxatiga faylni qo'shish
    data = await state.get_data()
    dependents = data.get("dependents", [])
    wife_dep = next((d for d in dependents if d.get("status") == "wife"), None)

    if wife_dep:
        wife_dep["passport_file"] = file_path
    else:
        # Agar wife hali qo‘shilmagan bo‘lsa
        dependents.append({
            "full_name": data.get("wife_full_name", "—"),
            "status": "wife",
            "passport_file": file_path,
            "photo_file": None
        })

    await state.update_data(dependents=dependents)

    await message.answer(
        "📸 Turmush o'rtog'ingizning fotosuratini yuboring (JPG, PNG, 2MB gacha):"
    )
    await state.set_state(ApplicationForm.wife_photo)


@router.message(ApplicationForm.wife_passport, ~F.document)
async def require_wife_passport_as_document(message: Message, state: FSMContext):
    await message.answer(
        "❗️ Iltimos, turmush o‘rtog‘ingiz pasportini **Fayl sifatida** yuboring (📎 *Attach* → *File*). "
        "Ruxsat etilgan turlar: .pdf, .jpg, .jpeg, .png. Hajm: 2MB gacha."
    )
