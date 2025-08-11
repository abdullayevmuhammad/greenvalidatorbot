from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.application import ApplicationForm

router = Router()

@router.message(ApplicationForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("📄 Endi pasport faylingizni yuboring (JPG, PNG yoki PDF, 2MB gacha):")
    await state.set_state(ApplicationForm.passport_file)
