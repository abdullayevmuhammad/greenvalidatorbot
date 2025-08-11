from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.file import get_download_path, safe_filename
from utils.validators import validate_file_extension, validate_file_size
from states.application import ApplicationForm
from utils.api import post_applicant

router = Router()

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
        await message.answer("❌ Fayl noto‘g‘ri. Faqat PDF, JPG, PNG (2MB gacha) yuboring.")
        return

    data = await state.get_data()
    current_child = data.get("current_child", 1)
    children_total = data.get("children_count", 0)

    # ✅ Oxirgi farzandga faylni biriktiramiz
    dependents = data.get("dependents", [])
    if dependents:
        dependents[-1]["passport_file"] = file_path
    await state.update_data(dependents=dependents)

    # 🔁 Yana farzand bo‘lsa, keyingisini so‘raymiz
    if current_child < children_total:
        next_child = current_child + 1
        await state.update_data(current_child=next_child)
        await message.answer(f"👶 {next_child}-farzandingizning to‘liq ismini kiriting:")
        await state.set_state(ApplicationForm.child_full_name)
        return

    # ✅ Barcha farzandlar tugadi — yuborishga tayyorlanamiz

    file_paths = {
        "passport_file": data.get("passport_file"),  # asosiy applicant
        "photo_file": data.get("photo_file")
    }

    # ✅ Fayllar `open()` qilinmaydi — faqat path yuboriladi
    resp = await post_applicant(data, file_paths)

    if resp.status_code == 201:
        await message.answer("✅ Arizangiz muvaffaqiyatli yuborildi.")
    else:
        await message.answer(f"❌ Xatolik: {resp.status_code}\n{resp.text}")

    await state.clear()

# handlers/applications/child_passport.py
@router.message(ApplicationForm.child_passport, ~F.document)
async def require_child_passport_as_document(message: Message, state: FSMContext):
    await message.answer(
        "❗️ Iltimos, farzandingiz pasportini **Fayl sifatida** yuboring (📎 *Attach* → *File*). "
        "Ruxsat etilgan turlar: .pdf, .jpg, .jpeg, .png. Hajm: 2MB gacha."
    )
