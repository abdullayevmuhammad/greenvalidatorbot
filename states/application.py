from aiogram.fsm.state import State, StatesGroup


class ApplicationForm(StatesGroup):
    full_name = State()
    passport_file = State()
    photo = State()
    phone_number = State()
    address = State()
    postal_code = State()
    email = State()
    address = State()          # Yangi qo'shiladigan
    postal_code = State()    
    education_level = State()
    marital_status = State()
    children_count = State()
    phone = State()
    wife_full_name = State()
    wife_passport = State()
    wife_photo = State()
    child_full_name = State()
    child_passport = State()  