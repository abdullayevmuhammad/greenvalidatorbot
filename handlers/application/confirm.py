from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm
from keyboards.confirm import confirm_keyboard
from utils.api import post_applicant

router = Router()

def _yn(ok: bool) -> str:
    return "✅" if ok else "—"

def _mask(s: str, keep: int = 4) -> str:
    if not s:
        return "—"
    s = s.strip()
    if len(s) <= keep:
        return s
    return f"{s[:keep]}•••{s[-2:]}"

def _humanize_edu(val: str) -> str:
    # Saqlanayotgan qiymatlar bo‘yicha moslab o‘zgartiring
    mapping = {
        "secondary": "O‘rta",
        "special_secondary": "O‘rta maxsus",
        "bachelor": "Bakalavr",
        "master": "Magistr",
        "phd": "PhD",
    }
    return mapping.get(val, val or "—")

def _humanize_ms(val: str) -> str:
    mapping = {"single": "Uylanmagan / Turmushga chiqmagan", "married": "Uylangan / Turmush qurgan", "divorced": "Ajrashgan"}
    return mapping.get(val, val or "—")

def _build_summary(data: dict) -> str:
    dependents = data.get("dependents", []) or []
    wife = next((d for d in dependents if d.get("status") == "wife"), None)
    children = [d for d in dependents if d.get("status") == "child"]

    lines = [
        "🧾 <b>Ariza ma’lumotlari</b>",
        "",
        f"👤 F.I.Sh.: <b>{data.get('full_name', '—')}</b>",
        f"📄 Pasport fayli: {_yn(bool(data.get('passport_file')))}",
        f"🖼 600×600 foto: {_yn(bool(data.get('photo_file')))}",
        f"📞 Telefon: <code>{_mask(data.get('phone_number', ''))}</code>",
        f"📧 Email: <code>{data.get('email') or '—'}</code>",
        f"🏠 Manzil: {data.get('address', '—')}",
        f"📬 Indeks: {data.get('postal_code', '—')}",
        f"🎓 Ta’lim: {_humanize_edu(data.get('education_level'))}",
        f"💍 Oilaviy holat: {_humanize_ms(data.get('marital_status'))}",
        "",
        "👨‍👩‍👧‍👦 <b>Oila a’zolari</b>",
        f"• Turmush o‘rtog‘i: {('—' if not wife else wife.get('full_name','—'))}",
        *(f"• Farzand: {c.get('full_name','—')}" for c in children),
        "",
        "Hammasi to‘g‘rimi? Tasdiqlang yoki bekor qiling.",
    ]
    return "\n".join(lines)

async def ask_confirmation(target: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = _build_summary(data)

    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=confirm_keyboard, parse_mode="HTML")
        await target.answer()
    else:
        await target.answer(text, reply_markup=confirm_keyboard, parse_mode="HTML")

    await state.set_state(ApplicationForm.confirm)


@router.callback_query(ApplicationForm.confirm, F.data == "confirm_send")
async def confirm_send(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    form_data = data.get("form_data") or data

    # Tugmalarni o'chirib qo'yamiz
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    # Faqat JSON ma'lumotlarni yuboramiz
    resp = await post_applicant(form_data)

    if resp.status_code == 201:
        await callback.message.answer("✅ Arizangiz muvaffaqiyatli yuborildi.")
        await state.clear()
    else:
        error_text = f"❌ Xatolik: {resp.status_code}"
        try:
            error_data = resp.json()
            if isinstance(error_data, dict):
                error_details = error_data.get('detail') or error_data.get('message') or str(error_data)
                error_text += f"\n{error_details}"
            else:
                error_text += f"\n{error_data}"
        except:
            # HTML yoki oddiy text
            from utils.api import clean_html_response  # Yangi funksiyani import qilamiz
            error_response = resp.text
            clean_error = clean_html_response(error_response)
            error_text += f"\n{clean_error[:300]}"  # 300 ta belgidan ortiq bo'lmasin

        await callback.message.answer(error_text, parse_mode=None)

    await callback.answer()


@router.callback_query(ApplicationForm.confirm, F.data == "cancel_send")
async def cancel_send(callback: CallbackQuery, state: FSMContext):
    # Tugmalarni olib tashlaymiz va formani boshidan boshlaymiz
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await state.clear()
    await callback.message.answer("❌ Bekor qilindi. Boshidan boshlaymiz.\n\n👤 Iltimos, to‘liq ismingizni kiriting:")
    await state.set_state(ApplicationForm.full_name)
    await callback.answer()
