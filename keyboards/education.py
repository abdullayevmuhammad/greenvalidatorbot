# tgbot/keyboards/education.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Callback -> Matn mapping
EDUCATION_LEVELS = {
    "edu_incomplete_school": "Maktabni tugatmagan (1–11 sinfni tugatmagan)",
    "edu_high_school": "Maktabni bitirgan (Umumiy o‘rta ta’lim)",
    "edu_vocational": "Kollej/Litseyni bitirgan",
    "edu_some_university": "Universitetda o‘qiyapti",
    "edu_bachelor": "Bakalavrni tugatgan",
    "edu_some_master": "Magistraturada o‘qiyapti",
    "edu_master": "Magistraturani tugatgan",
    "edu_some_phd": "Doktoranturada o‘qiyapti",
    "edu_phd": "Doktoranturani tugatgan (PhD)"
}

# Inline tugmalar
education_level_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📘 Maktabni tugatmagan\n(1–11 sinfni tugatmagan)", callback_data="edu_incomplete_school")],
        [InlineKeyboardButton(text="🎓 Maktabni bitirgan\n(Umumiy o‘rta ta’lim)", callback_data="edu_high_school")],
        [InlineKeyboardButton(text="🏫 Kollej/Litseyni bitirgan", callback_data="edu_vocational")],
        [InlineKeyboardButton(text="📖 Universitetda o‘qiyapti", callback_data="edu_some_university")],
        [InlineKeyboardButton(text="🎓 Bakalavrni tugatgan", callback_data="edu_bachelor")],
        [InlineKeyboardButton(text="📚 Magistraturada o‘qiyapti", callback_data="edu_some_master")],
        [InlineKeyboardButton(text="🎓 Magistraturani tugatgan", callback_data="edu_master")],
        [InlineKeyboardButton(text="📖 Doktoranturada o‘qiyapti", callback_data="edu_some_phd")],
        [InlineKeyboardButton(text="🎓 Doktoranturani tugatgan (PhD)", callback_data="edu_phd")],
    ]
)
