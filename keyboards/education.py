from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

education_level_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎓 Oliy", callback_data="edu_oliy")],
    [InlineKeyboardButton(text="🏫 O‘rta maxsus", callback_data="edu_orta_maxsus")],
    [InlineKeyboardButton(text="🏢 O‘rta", callback_data="edu_orta")],
    [InlineKeyboardButton(text="📘 Boshlang‘ich", callback_data="edu_boshlangich")]
])
