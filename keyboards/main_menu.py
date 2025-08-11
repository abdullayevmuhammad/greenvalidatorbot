# keyboards/main_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU_BUTTONS = {
    "about_bot": "ℹ️ Bot haqida ma'lumot",
    "about_gc": "🗽 Green Card haqida ma'lumot",
    "contact_admin": "👨‍💼 Admin bilan bog'lanish",
    "apply": "📝 Ariza yuborish",
    "get_code": "🔐 Confirmation kodni olish",
}

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=MAIN_MENU_BUTTONS["about_bot"]), KeyboardButton(text=MAIN_MENU_BUTTONS["about_gc"])],
        [KeyboardButton(text=MAIN_MENU_BUTTONS["contact_admin"])],
        [KeyboardButton(text=MAIN_MENU_BUTTONS["apply"])],
        [KeyboardButton(text=MAIN_MENU_BUTTONS["get_code"])],
    ],
    resize_keyboard=True,
    input_field_placeholder="Bo'limlardan birini tanlang…"
)
