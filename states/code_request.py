# states/code_request.py
from aiogram.fsm.state import StatesGroup, State

class CodeRequest(StatesGroup):
    wait_phone = State()
