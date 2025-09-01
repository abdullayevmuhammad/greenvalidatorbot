# handlers/common/start.py
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction

from keyboards.main_menu import main_menu_kb, MAIN_MENU_BUTTONS
from states.application import ApplicationForm
from states.code_request import CodeRequest           # ✅ NEW
from utils.api import get_confirmation_by_phone       # ✅ NEW

import re, os, tempfile                               # ✅ NEW

router = Router()

# /start da menyuni ko'rsatish
@router.message(CommandStart())
async def on_start(message: Message):
    await message.answer(
        "Assalomu alaykum! Botga xush kelibsiz! Bo'limlardan birini tanlang",
        reply_markup=main_menu_kb
    )

# a) Bot haqida ma'lumot
@router.message(F.text == MAIN_MENU_BUTTONS["about_bot"])
async def about_bot(message: Message):
    text = (
        """ℹ️ Bot haqida ma’lumot

Bu bot Green Card arizasi uchun ma’lumotlarni bosqichma-bosqich yig‘adi va tekshiradi. Ariza topshirishdan oldin quyidagilar tayyor bo‘lsin:

📄 Hujjatlar va cheklovlar
• Pasport fayli – PDF, JPG yoki PNG, hajmi 2 MB gacha. Fayl sifatida yuborilishi shart. (Tekshiruvlar: kengaytma va hajm limiti)
• Surat – 600×600 piksel, faqat JPG/JPEG/PNG, 2 MB gacha. Fayl sifatida yuboring (Telegram “photo” bo‘lmasligi kerak). O‘lchami aniq 600×600 ekanligi tekshiriladi.
• Barcha fayl nomlari 100 belgidan oshmasligi kerak (server cheklovi). Bot avtomatik ravishda xavfsiz qisqartiradi.

🧭 Ariza topshirish bosqichlari

To‘liq ism

Pasport fayli (PDF/JPG/PNG, ≤ 2 MB)

600×600 surat (JPG/PNG, ≤ 2 MB)

Telefon raqami (+998XXXXXXXXX)

Email — ixtiyoriy. Xohlasangiz O‘tkazib yuborish tugmasi orqali bo‘sh qoldirishingiz mumkin.

To‘liq manzil, so‘ngra pochta indeksi

Ta’lim darajasi (inline tugmalar orqali)

Oilaviy holat:
 • Bo‘ydoq – farzandlar bo‘lmasa, ariza darhol yuboriladi
 • Uylangan – turmush o‘rtog‘i ma’lumoti va fayllari so‘raladi
 • Ajrashgan – to‘g‘ridan-to‘g‘ri farzandlar soni bosqichiga o‘tiladi

Farzandlar soni – agar N > 0 bo‘lsa, har biri uchun ism va pasport/tug‘ilganlik guvohnomasi fayli (PDF/JPG/PNG, ≤ 2 MB) so‘raladi

👥 Turmush o‘rtog‘i va farzandlar (dependents)
• Turmush o‘rtog‘i – pasport (PDF/JPG/PNG, ≤ 2 MB) va 600×600 surat (fayl sifatida)
• Farzandlar – ism va pasport/tug‘ilganlik guvohnomasi fayli (PDF/JPG/PNG, ≤ 2 MB)

🧾 Confirmation kod – telefon raqami orqali tekshiruv ulanadi.

▶️ Boshlash uchun — 📝 Ariza yuborish tugmasini bosing."""
    )
    await message.answer(text=text, reply_markup=main_menu_kb)

# b) Green Card haqida ma'lumot
@router.message(F.text == MAIN_MENU_BUTTONS["about_gc"])
async def about_gc(message: Message):
    text = """🗽 Green Card haqida qisqacha

Green Card — bu AQShda doimiy yashash va ishlash huquqini beradigan karta. Har yili AQSh Davlat Departamenti Diversity Visa Lottery (lotereya) o‘tkazadi.

✅ Ishtirok etish jarayoni:

Har yili oktyabr oyida rasmiy ariza qabul qilish boshlanadi (taxminan 1 oy davom etadi).

Ariza faqat rasmiy sayt orqali topshiriladi (hech qanday to‘lov olinmaydi).

Faqat bitta ariza topshirish mumkin — ko‘p marta topshirish diskvalifikatsiya qiladi.

Fotosurat va shaxsiy ma’lumotlar qat’iy talablar bo‘yicha topshiriladi.

Natijalar odatda keyingi yil may oyida e’lon qilinadi.

ℹ️ Ushbu bot — rasmiy ariza topshirish vositasi emas. U sizning ma’lumotlaringizni tayyorlab, rasmiy talablarga mos formatda jamlaydi."""
    await message.answer(text=text, reply_markup=main_menu_kb)

# c) Admin bilan bog'lanish
@router.message(F.text == MAIN_MENU_BUTTONS["contact_admin"])
async def contact_admin(message: Message):
    await message.answer(
        "Admin bilan bog'lanish: @Ozoddeee\nTelefon: +998 90 799 79 07",
        reply_markup=main_menu_kb
    )

# d) Ariza yuborish — FSM ni boshlash
@router.message(F.text == MAIN_MENU_BUTTONS["apply"])
async def start_application_flow(message: Message, state: FSMContext):
    await message.answer("👤 To‘liq ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ApplicationForm.full_name)

# e) 🔐 Confirmation kodni olish — TELEFON so'rash (PLACEHOLDER o'rniga)
@router.message(F.text == MAIN_MENU_BUTTONS["get_code"])
async def ask_phone(message: Message, state: FSMContext):
    await message.answer(
        "📞 Telefon raqamingizni yuboring (masalan: <code>+998901234567</code>):",
        reply_markup=main_menu_kb,
        parse_mode="HTML"
    )
    await state.set_state(CodeRequest.wait_phone)

# f) Telefon qabul qilish va faylni yuborish
PHONE_RE = re.compile(r'^\+998\d{9}$')

@router.message(CodeRequest.wait_phone, F.text)
async def fetch_confirmation_by_phone(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    # Normalizatsiya: bo'sh joy, tire, qavslarni olib tashlaymiz
    phone = re.sub(r'[^\d+]', '', raw)

    if not PHONE_RE.fullmatch(phone):
        await message.answer(
            "❗️ Noto‘g‘ri format.\nIltimos, <code>+998XXXXXXXXX</code> ko‘rinishida yuboring.",
            parse_mode="HTML"
        )
        return

    try:
        await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)
    except Exception:
        pass

    status, content, filename = await get_confirmation_by_phone(phone)

    if status == 200 and content:
        tmp = tempfile.gettempdir()
        path = os.path.join(tmp, filename)
        with open(path, "wb") as f:
            f.write(content)
        try:
            await message.answer_document(
                FSInputFile(path, filename=filename),
                caption="🔐 Confirmation faylingiz ilovada.",
                parse_mode=None
            )
        finally:
            try: os.remove(path)
            except: pass
        await state.clear()
        return

    if status == 404:
        await message.answer(
            "❗️ Ushbu telefon raqam bo‘yicha confirmation topilmadi.\n"
            "Raqamni tekshirib, qayta urinib ko‘ring.",
            parse_mode=None
        )
    else:
        await message.answer(
            f"❌ Xatolik: {status}\nIltimos, keyinroq qayta urinib ko‘ring.",
            parse_mode=None
        )
    # State saqlanadi — foydalanuvchi boshqa raqam yuborishi mumkin.
