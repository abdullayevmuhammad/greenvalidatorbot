from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm
from .confirm import ask_confirmation

router = Router()

@router.message(ApplicationForm.children_count)
async def handle_children_count(message: Message, state: FSMContext):
    try:
        count = int(message.text)
        if count < 0:
            raise ValueError("Son manfiy bo'lishi mumkin emas")

        await state.update_data(children_count=count)

        data = await state.get_data()
        dependents = data.get("dependents", [])

        if count > 0:
            # ➕ Farzandlar bo‘lsa, ularning ma’lumotlarini so‘rash
            await message.answer(f"👶 Iltimos, 1-farzandingizning to‘liq ismini kiriting:")
            await state.update_data(current_child=1, dependents=dependents)
            await state.set_state(ApplicationForm.child_full_name)
        else:
            # ✅ Farzand yo‘q — arizani darhol yuboramiz
            await state.update_data(dependents=dependents)  # bo‘sh ro‘yxat
            await ask_confirmation(message, state)

    except ValueError:
        await message.answer("❌ Noto'g'ri format. Iltimos, faqat raqam kiriting (masalan: 2)")
