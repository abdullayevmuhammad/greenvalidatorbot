from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import os

from states.application import ApplicationForm
from utils.file import get_download_path, safe_filename
from utils.validators import validate_file_extension, validate_file_size

router = Router()

@router.message(ApplicationForm.wife_passport, F.document)
async def handle_wife_passport_document(message: Message, state: FSMContext):

    file = message.document
    safe_name = safe_filename(file.file_id, file.file_name, max_length=100)
    file_path = get_download_path(safe_name)
    try:
        # Faylni yuklab olish
        await message.bot.download(file, destination=file_path)

        # Validatsiya (kenaytma va hajm)
        validate_file_extension(safe_name)
        validate_file_size(file.file_size)

    except ValueError as e:
        await message.answer(f"❌ Turmush o‘rtog‘i pasport faylida xatolik:\n{e}")
        return
    except Exception as e:
        await message.answer("❌ Turmush o‘rtog‘i pasport faylini yuklab olishda xatolik yuz berdi.")
        print(f"[ERROR] Wife passport download error: {e}")
        return

    # Faylni state ga saqlaymiz
    await state.update_data(wife_passport_file=file_path)

    await message.answer("🖼 Endi turmush o‘rtog‘ingizning 600x600 o‘lchamdagi fotosuratini yuboring:")
    await state.set_state(ApplicationForm.wife_photo)

# handlers/applications/wife_passport.py
@router.message(ApplicationForm.wife_passport, ~F.document)
async def require_wife_passport_as_document(message: Message, state: FSMContext):
    await message.answer(
        "❗️ Iltimos, turmush o‘rtog‘ingiz pasportini **Fayl sifatida** yuboring (📎 *Attach* → *File*). "
        "Ruxsat etilgan turlar: .pdf, .jpg, .jpeg, .png. Hajm: 2MB gacha."
    )