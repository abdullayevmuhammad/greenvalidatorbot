from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

marital_status_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💍 Uylangan / Turmushga chiqqan", callback_data="married")],
    [InlineKeyboardButton(text="🧑‍💼 Bo‘ydoq / Yolg‘iz", callback_data="single")],
    [InlineKeyboardButton(text="❌ Ajrashgan", callback_data="divorced")],  # ✅ yangi
])
