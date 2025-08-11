from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm
from utils.api import post_applicant

router = Router()

@router.message(ApplicationForm.children_count)
async def handle_children_count(message: Message, state: FSMContext):
    try:
        count = int(message.text)
        if count < 0:
            raise ValueError("Son manfiy bo'lishi mumkin emas")

        await state.update_data(children_count=count)

        if count > 0:
            # ➕ Farzandlar bo‘lsa, ularning ma’lumotlarini so‘rash
            await message.answer(f"👶 Iltimos, 1-farzandingizning to‘liq ismini kiriting:")
            await state.update_data(current_child=1)
            await state.set_state(ApplicationForm.child_full_name)

        else:
            # ✅ Farzand yo‘q — arizani darhol yuboramiz
            data = await state.get_data()

            file_paths = {
                "passport_file": data.get("passport_file"),
                "photo_file": data.get("photo_file"),
            }

            resp = await post_applicant(data, file_paths)

            if resp.status_code == 201:
                await message.answer("✅ Arizangiz muvaffaqiyatli yuborildi.")
            else:
                await message.answer(f"❌ Xatolik: {resp.status_code}\n{resp.text}")

            await state.clear()

    except ValueError:
        await message.answer("❌ Noto'g'ri format. Iltimos, faqat raqam kiriting (masalan: 2)")
