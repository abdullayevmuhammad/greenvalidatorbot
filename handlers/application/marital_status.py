# tgbot/handlers/applcation/marital_status.py
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm
from .confirm import ask_confirmation

router = Router()


@router.callback_query(ApplicationForm.marital_status)
async def handle_marital(callback: CallbackQuery, state: FSMContext):
    choice = callback.data
    mapping = {'single': 'single', 'married': 'married', 'divorced': 'divorced'}

    if choice not in mapping:
        await callback.answer("❌ Noto'g'ri tanlov.", show_alert=True)
        return

    status = mapping[choice]
    await state.update_data(marital_status=status)
    await callback.message.delete_reply_markup()

    if status == "married":
        await callback.message.answer("Turmush o'rtog'ingizning to'liq ismini kiriting (F. I. Sh):")
        await state.set_state(ApplicationForm.wife_full_name)

    elif status == "divorced":
        await callback.message.answer(
            "👶 Farzandlaringiz sonini kiriting (agar farzandingiz bo'lmasa 0 deb yozing):"
        )
        await state.set_state(ApplicationForm.children_count)

    else:  # single
        data = await state.get_data()

        # Faqat kerakli ma'lumotlarni yuboramiz
        form_data = {
            "full_name": data["full_name"],
            "email": data.get("email", ""),
            "education_level": data["education_level"],
            "postal_code": data["postal_code"],
            "address": data["address"],
            "marital_status": status,
            "children_count": 0,  # Raqam sifatida
            "phone_number": data["phone_number"],
            "dependents": [],  # Single bo'lsa dependents yo'q
        }

        await state.update_data(form_data=form_data)
        await ask_confirmation(callback, state)