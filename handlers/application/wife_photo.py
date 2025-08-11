# handlers/applications/wife_photo.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm
from utils.file import get_download_path, safe_filename
from utils.validators import validate_file_extension, validate_file_size
from PIL import Image, UnidentifiedImageError
import os

router = Router()

@router.message(ApplicationForm.wife_photo, F.document)
async def handle_wife_photo_document(message: Message, state: FSMContext):
    file = message.document
    ext = os.path.splitext(file.file_name)[1].lower()

    # Faqat rasm turlariga ruxsat
    if ext not in [".jpg", ".jpeg", ".png"]:
        await message.answer("❌ Rasm faqat .jpg/.jpeg/.png bo‘lishi kerak. Iltimos, rasmni *Fayl sifatida* yuboring.")
        return

    # Fayl nomini xavfsiz qisqartirish (≤100)
    safe_name = safe_filename(file.file_id, file.file_name, max_length=100)
    file_path = get_download_path(safe_name)

    try:
        # Yuklab olish
        await message.bot.download(file, destination=file_path)

        # Validatsiya: kengaytma va hajm
        validate_file_extension(safe_name)
        validate_file_size(file.file_size)

        # O‘lcham: 600x600
        with Image.open(file_path) as img:
            w, h = img.size
            if (w, h) != (600, 600):
                await message.answer(f"❌ Rasm o‘lchami {w}x{h}. Iltimos, 600x600 piksel yuboring.")
                return

    except UnidentifiedImageError:
        await message.answer("❌ Rasmni o‘qib bo‘lmadi. Iltimos, haqiqiy .jpg/.jpeg/.png fayl yuboring.")
        return
    except ValueError as e:
        await message.answer(f"❌ Rasmda xatolik:\n{e}")
        return
    except Exception as e:
        await message.answer("❌ Turmush o‘rtog‘i rasm faylini tekshirishda xatolik yuz berdi.")
        print(f"[ERROR] Wife photo error: {e}")
        return

    # State ga saqlaymiz
    await state.update_data(wife_photo_file=file_path)

    # dependents ga qo‘shamiz
    data = await state.get_data()
    wife = {
        "full_name": data.get("wife_full_name"),
        "status": "wife",
        "passport_file": data.get("wife_passport_file"),
        "photo_file": file_path,
    }
    dependents = data.get("dependents", [])
    dependents.append(wife)
    await state.update_data(dependents=dependents)

    await message.answer("👶 Endi farzandlaringiz sonini kiriting (agar farzandingiz bo‘lmasa 0 deb yozing):")
    await state.set_state(ApplicationForm.children_count)

@router.message(ApplicationForm.wife_photo, ~F.document)
async def require_wife_photo_as_document(message: Message, state: FSMContext):
    await message.answer(
        "❗️ Iltimos, turmush o‘rtog‘ingiz rasmni **Fayl sifatida** yuboring (📎 *Attach* → *File*). "
        "Faqat .jpg/.jpeg/.png va o‘lcham 600x600."
    )
