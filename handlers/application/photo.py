# tgbot/handlers/applcation/photo.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from PIL import Image, UnidentifiedImageError
import os

from states.application import ApplicationForm
from utils.file import get_download_path, safe_filename
from utils.validators import validate_file_extension, validate_file_size

router = Router()

# ✅ Rasm faqat DOCUMENT sifatida qabul qilinadi
# tgbot/handlers/applcation/photo.py
@router.message(ApplicationForm.photo, F.document)
async def handle_photo_document(message: Message, state: FSMContext):
    file = message.document
    ext = os.path.splitext(file.file_name)[1].lower()

    # Faqat rasm turlari
    if ext not in [".jpg", ".jpeg", ".png"]:
        await message.answer("❌ Rasm faqat .jpg/.jpeg/.png bo'lishi kerak. Iltimos, rasmni *Fayl sifatida* yuboring.")
        return

    # Fayl nomini xavfsiz qisqartirish (≤100)
    safe_name = safe_filename(file.file_id, file.file_name, max_length=100)
    file_path = get_download_path(safe_name)

    try:
        # Yuklab olish
        await message.bot.download(file, destination=file_path)

        # Validatsiya: kengaytma va hajm
        validate_file_extension(safe_name)  # ext safe_name'dan olinadi
        validate_file_size(file.file_size)  # document hajmi

        # O'lcham tekshiruv (600x600)
        with Image.open(file_path) as img:
            w, h = img.size
            if (w, h) != (600, 600):
                await message.answer(f"❌ Rasm o'lchami {w}x{h}. Iltimos, aynan 600x600 piksel bo'lsin.")
                return

    except UnidentifiedImageError:
        await message.answer("❌ Rasmni o'qib bo'lmadi. Iltimos, haqiqiy .jpg/.jpeg/.png fayl yuboring.")
        return
    except ValueError as e:
        await message.answer(f"❌ Rasmda xatolik:\n{e}")
        return
    except Exception as e:
        await message.answer("❌ Rasmni tekshirishda xatolik yuz berdi.")
        print(f"[ERROR] Photo check error: {e}")
        return

    # State ni yangilash - ikkala kalit bilan ham saqlaymiz
    await state.update_data({
        "photo_file": file_path,
        "photo": file_path  # Qo'shimcha kalit
    })

    await message.answer("📞 Endi telefon raqamingizni yuboring (masalan: +998901234567):")
    await state.set_state(ApplicationForm.phone_number)


# ❗️Fallback: document bo‘lmasa — yo‘l-yo‘riq beramiz
@router.message(ApplicationForm.photo, ~F.document)
async def require_photo_as_document(message: Message, state: FSMContext):
    await message.answer(
        "❗️ Iltimos, rasmni Fayl sifatida yuboring (📎 *Attach* → *File*). "
        "Faqat .jpg/.jpeg/.png va o‘lcham aynan 600x600 bo‘lsin."
    )
