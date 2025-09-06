# tgbot/handlers/applcation/passport.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm
from utils.file import get_download_path, safe_filename
from utils.validators import validate_file_extension, validate_file_size  # ✅ Yangi validatorlar

router = Router()


@router.message(ApplicationForm.passport_file, F.document)
async def get_passport_document(message: Message, state: FSMContext):
    file = message.document
    safe_name = safe_filename(file.file_id, file.file_name, max_length=100)
    file_path = get_download_path(safe_name)
    try:
        await message.bot.download(file, destination=file_path)
        validate_file_extension(safe_name)
        validate_file_size(file.file_size)
    except ValueError as e:
        await message.answer(str(e))
        return
    except Exception as e:
        await message.answer("❌ Faylni yuklab olishda xatolik yuz berdi.")
        print(f"[ERROR] Passport file download: {e}")
        return

    await state.update_data(passport_file=file_path)
    await message.answer("🖼 Endi 600x600 o‘lchamdagi fotosurat yuboring (shu kunlarda tushgan yangi suratingiz bo'lishi kerak):")
    await state.set_state(ApplicationForm.photo)

# handlers/applications/passport.py
@router.message(ApplicationForm.passport_file, ~F.document)
async def require_passport_as_document(message: Message, state: FSMContext):
    await message.answer(
        "❗️ Iltimos, pasportni **Fayl sifatida** yuboring (📎 *Attach* → *File*). "
        "Ruxsat etilgan turlar: .pdf, .jpg, .jpeg, .png. Hajm: 2MB gacha."
    )
