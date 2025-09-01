# handlers/application/get_code_by_phone.py
import os
import re
import tempfile
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram.enums import ChatAction

from keyboards.main_menu import MAIN_MENU_BUTTONS
from states.code_request import CodeRequest
from utils.api import get_confirmation_by_phone, phone_exists

# Admin kontaktini configdan olish tavsiya:
try:
    from config import SUPPORT_CONTACT_HTML
except Exception:
    SUPPORT_CONTACT_HTML = (
        "\n\n📞 Admin: +998xx xxx xx xx\n"
        "✉️ Telegram: @your_admin\n"
        "⏰ Ish vaqti: 09:00–18:00"
    )

router = Router()
PHONE_RE = re.compile(r'^\+998\d{9}$')

def _with_support(msg: str) -> str:
    # Har bir xabarning pastiga admin kontaktini qo'shamiz
    return msg + SUPPORT_CONTACT_HTML

@router.message(F.text == MAIN_MENU_BUTTONS["get_code"])
async def ask_phone(message: Message, state: FSMContext):
    await message.answer(
        "📞 Telefon raqamingizni yuboring (masalan: <code>+998901234567</code>):",
        parse_mode="HTML"
    )
    await state.set_state(CodeRequest.wait_phone)
@router.message(CodeRequest.wait_phone, F.text)
async def fetch_and_send_confirmation(message: Message, state: FSMContext):
    phone = (message.text or "").strip()

    if not PHONE_RE.fullmatch(phone):
        await message.answer(
            _with_support("❗️ Noto‘g‘ri format.\nIltimos, <code>+998XXXXXXXXX</code> ko‘rinishida yuboring."),
            parse_mode="HTML"
        )
        return

    try:
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass

    # >>> YANGI: tri-holatli tekshiruv
    status_exists, exists = await phone_exists(phone)

    if status_exists == 200 and exists is False:
        await message.answer(
            _with_support("ℹ️ Ushbu telefon raqami bo‘yicha ariza topilmadi (ro‘yxatdan o‘tmagan)."),
            parse_mode="HTML"
        )
        return

    if status_exists in (401, 403):
        await message.answer(
            _with_support("🔒 Ruxsat berilmadi. Serverga autentifikatsiya (TOKEN) talab qilinadi."),
            parse_mode="HTML"
        )
        return

    if status_exists != 200 or exists is None:
        # xizmat vaqtincha muammo: 5xx, 404, 502, 503 va h.k.
        await message.answer(
            _with_support(f"⚠️ Xizmat vaqtincha mavjud emas (status: {status_exists}). Keyinroq urinib ko‘ring."),
            parse_mode="HTML"
        )
        return

    # Bu yerga faqat (200, True) bilan keladi → faylni olishga harakat qilamiz
    status, content, filename = await get_confirmation_by_phone(phone)

    if status == 200 and content:
        lower = filename.lower()
        action = ChatAction.UPLOAD_PHOTO if lower.endswith((".png", ".jpg", ".jpeg")) else ChatAction.UPLOAD_DOCUMENT
        try:
            await message.bot.send_chat_action(message.chat.id, action)
        except Exception:
            pass

        tmp_dir = tempfile.gettempdir()
        path = os.path.join(tmp_dir, filename)
        with open(path, "wb") as f:
            f.write(content)

        try:
            if lower.endswith((".png", ".jpg", ".jpeg")):
                await message.answer_photo(
                    FSInputFile(path, filename=filename),
                    caption="🔐 Confirmation rasmingiz ilovada."
                )
            else:
                await message.answer_document(
                    FSInputFile(path, filename=filename),
                    caption="🔐 Confirmation faylingiz ilovada."
                )
        finally:
            try: os.remove(path)
            except Exception: pass

        await state.clear()
        return

    if status == 404:
        await message.answer(
            _with_support("⌛️ Arizangiz topildi, biroq kod/fayl hali joylanmagan."),
            parse_mode="HTML"
        )
        return

    if status in (401, 403):
        await message.answer(
            _with_support("🔒 Ruxsat berilmadi. Iltimos, tizimga autentifikatsiya (TOKEN) sozlanganini tekshiring."),
            parse_mode="HTML"
        )
        return

    if status == 415:
        await message.answer(
            _with_support("⚠️ Server kutilmagan kontent yubordi (PDF/PNG/JPG emas). Iltimos, keyinroq urinib ko‘ring."),
            parse_mode="HTML"
        )
        return

    await message.answer(
        _with_support(f"❌ Xatolik: {status}\nIltimos, keyinroq qayta urinib ko‘ring."),
        parse_mode="HTML"
    )