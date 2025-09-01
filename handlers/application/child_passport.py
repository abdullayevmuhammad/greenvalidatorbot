from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.file import get_download_path, safe_filename
from utils.validators import validate_file_extension, validate_file_size
from states.application import ApplicationForm
from .confirm import ask_confirmation

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

    dependents = data.get("dependents", [])

    # ✅ Farzand ma’lumotini yangilash yoki qo‘shish
    if len(dependents) < current_child:
        dependents.append({
            "full_name": data.get("child_full_name", "—"),
            "status": "child",
            "passport_file": file_path
        })
    else:
        dependents[current_child-1]["passport_file"] = file_path

    await state.update_data(dependents=dependents)

    # 🔁 Yana farzand bo‘lsa, keyingisini so‘raymiz
    if current_child < children_total:
        next_child = current_child + 1
        await state.update_data(current_child=next_child)
        await state.set_state(ApplicationForm.child_full_name)
        await message.answer(f"👶 {next_child}-farzandingizning to‘liq ismini kiriting:")
        return

    # ✅ Barcha farzandlar tugadi — arizani yuborishga tayyorlanamiz
    await ask_confirmation(message, state)


@router.message(ApplicationForm.child_passport, ~F.document)
async def require_child_passport_as_document(message: Message, state: FSMContext):
    await message.answer(
        "❗️ Iltimos, farzandingiz pasportini **Fayl sifatida** yuboring (📎 *Attach* → *File*). "
        "Ruxsat etilgan turlar: .pdf, .jpg, .jpeg, .png. Hajm: 2MB gacha."
    )
