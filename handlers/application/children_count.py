# tgbot/handlers/application/children_count.py
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm
from .confirm import ask_confirmation

router = Router()


# tgbot/handlers/application/children_count.py
@router.message(ApplicationForm.children_count)
async def handle_children_count(message: Message, state: FSMContext):
    try:
        count = int(message.text)
        if count < 0:
            raise ValueError("Son manfiy bo'lishi mumkin emas")

        data = await state.get_data()

        # Xotin ma'lumotlarini saqlab qolish
        dependents = data.get("dependents", [])
        wife_dep = next((d for d in dependents if d.get("status") == "wife"), None)

        # Yangi dependents ro'yxatini yaratamiz (faqat xotin)
        new_dependents = []
        if wife_dep:
            new_dependents.append(wife_dep)

        await state.update_data({
            "children_count": count,
            "dependents": new_dependents,
            "current_child": 1
        })

        if count > 0:
            await message.answer(f"👶 Iltimos, 1-farzandingizning to'liq ismini kiriting:")
            await state.set_state(ApplicationForm.child_full_name)
        else:
            await ask_confirmation(message, state)

    except ValueError:
        await message.answer("❌ Noto'g'ri format. Iltimos, faqat raqam kiriting (masalan: 2)")