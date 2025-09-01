from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_send")],
    [InlineKeyboardButton(text="↩️ Bekor qilish", callback_data="cancel_send")]
])
