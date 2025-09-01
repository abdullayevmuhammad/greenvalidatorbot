# tgbot/handlers/application/confirm.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm
from keyboards.confirm import confirm_keyboard
from utils.api import post_applicant, post_dependent

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
    mapping = {
        "secondary": "O‘rta",
        "special_secondary": "O‘rta maxsus",
        "bachelor": "Bakalavr",
        "master": "Magistr",
        "phd": "PhD",
    }
    return mapping.get(val, val or "—")

def _humanize_ms(val: str) -> str:
    mapping = {
        "single": "Uylanmagan / Turmushga chiqmagan",
        "married": "Uylangan / Turmush qurgan",
        "divorced": "Ajrashgan"
    }
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

    # 1) Applicant form fields
    form_data = {
        "full_name": data.get("full_name"),
        "address": data.get("address"),
        "postal_code": data.get("postal_code"),
        "email": data.get("email") or "",
        "education_level": data.get("education_level"),
        "marital_status": data.get("marital_status"),
        "children_count": int(data.get("children_count") or 0),
        "phone_number": data.get("phone_number"),
    }

    # 2) Applicant files
    file_paths = {}
    if data.get("passport_file"):
        file_paths["passport_file"] = data.get("passport_file")
    if data.get("photo_file"):
        file_paths["photo"] = data.get("photo_file")

    # remove inline buttons
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    # 3) Create applicant
    status, body, applicant_id = await post_applicant(form_data, file_paths)

    if status in (200, 201) and applicant_id:
        # 4) Create dependents one-by-one (if any)
        errors = []
        for dep in data.get("dependents", []):
            if not isinstance(dep, dict):
                continue
            # ensure minimal fields
            dep_payload = {
                "full_name": dep.get("full_name"),
                "status": dep.get("status"),
                # include file paths if present in state
            }
            if dep.get("passport_file"):
                dep_payload["passport_file"] = dep.get("passport_file")
            if dep.get("photo_file"):
                dep_payload["photo"] = dep.get("photo_file")

            d_status, d_body = await post_dependent(dep_payload, applicant_id)
            if d_status not in (200, 201):
                errors.append({"dependent": dep_payload.get("full_name"), "status": d_status, "body": d_body})

        if not errors:
            await callback.message.answer("✅ Arizangiz muvaffaqiyatli yuborildi.")
            await state.clear()
        else:
            await callback.message.answer(f"✅ Applicant yaratildi, ammo dependents yuborishda xatoliklar:\n{errors}")
    else:
        # Show backend error (body may be dict or text)
        await callback.message.answer(f"❌ Applicant yuborishda xatolik: {status}\n{body}")

    await callback.answer()


@router.callback_query(ApplicationForm.confirm, F.data == "cancel_send")
async def cancel_send(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await state.clear()
    await callback.message.answer("❌ Bekor qilindi. Boshidan boshlaymiz.\n\n👤 Iltimos, to‘liq ismingizni kiriting:")
    await state.set_state(ApplicationForm.full_name)
    await callback.answer()
