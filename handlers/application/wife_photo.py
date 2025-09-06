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

# handlers/applications/wife_photo.py
@router.message(ApplicationForm.wife_photo, F.document)
async def handle_wife_photo_document(message: Message, state: FSMContext):
    file = message.document
    ext = os.path.splitext(file.file_name)[1].lower()

    if ext not in [".jpg", ".jpeg", ".png"]:
        await message.answer(
            "❌ Rasm faqat .jpg/.jpeg/.png bo‘lishi kerak. Iltimos, rasmni *Fayl sifatida* yuboring."
        )
        return

    safe_name = safe_filename(file.file_id, file.file_name, max_length=100)
    file_path = get_download_path(safe_name)

    try:
        await message.bot.download(file, destination=file_path)
        validate_file_extension(safe_name)
        validate_file_size(file.file_size)

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

    data = await state.get_data()
    dependents = data.get("dependents", [])
    wife_name = data.get("wife_full_name", "Turmush o'rtog'i")
    wife_passport = data.get("wife_passport_file")

    # Xotin ma'lumotlarini yangilash
    wife_index = None
    for i, dep in enumerate(dependents):
        if dep.get("status") == "wife":
            wife_index = i
            break

    if wife_index is not None:
        # Xotin allaqachon mavjud, yangilaymiz
        dependents[wife_index]["photo_file"] = file_path
    else:
        # Yangi xotin qo'shamiz
        dependents.append({
            "full_name": wife_name,
            "status": "wife",
            "passport_file": wife_passport,
            "photo_file": file_path,
        })

    await state.update_data(
        wife_photo_file=file_path,
        dependents=dependents
    )

    await message.answer(
        "👶 Endi farzandlaringiz sonini kiriting (agar farzandingiz bo‘lmasa 0 deb yozing):"
    )
    await state.set_state(ApplicationForm.children_count)