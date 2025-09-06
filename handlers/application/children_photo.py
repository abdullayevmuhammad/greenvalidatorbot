# tgbot/handlers/application/child_photo.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm
from utils.file import get_download_path, safe_filename
from utils.validators import validate_file_extension, validate_file_size
from PIL import Image, UnidentifiedImageError
import os

router = Router()


# tgbot/handlers/application/child_photo.py
@router.message(ApplicationForm.child_photo, F.document)
async def handle_child_photo_document(message: Message, state: FSMContext):
    file = message.document
    ext = os.path.splitext(file.file_name)[1].lower()

    if ext not in [".jpg", ".jpeg", ".png"]:
        await message.answer("❌ Rasm faqat .jpg/.jpeg/.png bo'lishi kerak. Iltimos, rasmni *Fayl sifatida* yuboring.")
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
                await message.answer(f"❌ Rasm o'lchami {w}x{h}. Iltimos, 600x600 piksel yuboring.")
                return

    except UnidentifiedImageError:
        await message.answer("❌ Rasmni o'qib bo'lmadi. Iltimos, haqiqiy .jpg/.jpeg/.png fayl yuboring.")
        return
    except ValueError as e:
        await message.answer(f"❌ Rasmda xatolik:\n{e}")
        return
    except Exception as e:
        await message.answer("❌ Farzand rasm faylini tekshirishda xatolik yuz berdi.")
        print(f"[ERROR] Child photo error: {e}")
        return

    data = await state.get_data()
    current_child = data.get("current_child", 1)
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
        dependents[child_index]["photo_file"] = file_path
    else:
        # Yangi farzand qo'shamiz
        dependents.append({
            "full_name": data.get(f"child_{current_child}_name", f"Farzand {current_child}"),
            "status": "child",
            "photo_file": file_path,
            "passport_file": None
        })

    await state.update_data({
        "dependents": dependents,
        f"child_{current_child}_photo": file_path
    })

    await message.answer(
        f"📄 Endi {current_child}-farzandingizning tug'ilganlik guvohnomasi yoki pasport faylini yuboring (PDF, JPG yoki PNG, 2MB gacha):")
    await state.set_state(ApplicationForm.child_passport)