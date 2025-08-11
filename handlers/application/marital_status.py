# handlers/applications/marital_status.py
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm
from utils.api import post_applicant

router = Router()

@router.callback_query(ApplicationForm.marital_status)
async def handle_marital(callback: CallbackQuery, state: FSMContext):
    choice = callback.data
    mapping = {'single': 'single', 'married': 'married', 'divorced': 'divorced'}  # ✅ Yangi status

    if choice not in mapping:
        await callback.answer("❌ Noto‘g‘ri tanlov.", show_alert=True)
        return

    status = mapping[choice]
    await state.update_data(marital_status=status)
    await callback.message.delete_reply_markup()

    if status == "married":
        # oldingi mantiqni saqlaymiz
        await callback.message.answer("Turmush o‘rtog‘ingizning to‘liq ismini kiriting:")
        await state.set_state(ApplicationForm.wife_full_name)

    elif status == "divorced":
        # ✅ Ajrashgan bo‘lsa — to‘g‘ridan-to‘g‘ri farzandlar soniga
        await callback.message.answer("👶 Farzandlaringiz sonini kiriting (agar farzandingiz bo‘lmasa 0 deb yozing):")
        await state.set_state(ApplicationForm.children_count)

    else:  # single
        data = await state.get_data()

        form_data = {
            "full_name": data["full_name"],
            "email": data.get("email", ""),
            "education_level": data["education_level"],
            "postal_code": data["postal_code"],
            "address": data["address"],
            "marital_status": status,
            "children_count": "0",
            "phone_number": data["phone_number"],
            "dependents": []
        }
        files = {
            "passport_file": data.get("passport_file"),
            "photo_file": data.get("photo_file"),
        }

        resp = await post_applicant(form_data, files)
        if resp.status_code == 201:
            await callback.message.answer("✅ Arizangiz muvaffaqiyatli yuborildi.")
        else:
            await callback.message.answer(f"❌ Xatolik: {resp.status_code}\n{resp.text}")

        await state.clear()

    await callback.answer()
