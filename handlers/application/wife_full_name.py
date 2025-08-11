from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm

router = Router()

@router.message(ApplicationForm.wife_full_name)
async def handle_wife_full_name(message: Message, state: FSMContext):
    await state.update_data(wife_full_name=message.text)
    await message.answer("📄 Turmush o'rtog'ingizning pasport faylini yuboring (JPG, PNG yoki PDF, 2MB gacha):")
    await state.set_state(ApplicationForm.wife_passport)