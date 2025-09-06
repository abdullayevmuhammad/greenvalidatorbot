# tgbot/handlers/application/confirm.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.application import ApplicationForm
from keyboards.confirm import confirm_keyboard
from utils.api import post_applicant, post_dependent
import os
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

# tgbot/handlers/application/confirm.py
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
        f"📞 Telefon: <code>{(data.get('phone_number', ''))}</code>",
        f"📧 Email: <code>{data.get('email') or '—'}</code>",
        f"🏠 Manzil: {data.get('address', '—')}",
        f"📬 Indeks: {data.get('postal_code', '—') or '—'}",
        f"🎓 Ta’lim: {_humanize_edu(data.get('education_level'))}",
        f"💍 Oilaviy holat: {_humanize_ms(data.get('marital_status'))}",
        "",
        "👨‍👩‍👧‍👦 <b>Oila a’zolari</b>",
        f"• Turmush o‘rtog‘i: {wife.get('full_name', '—') if wife else '—'}",
        *(f"• Farzand: {c.get('full_name','—')}" for c in children),
        "",
        "Arizangiz admin tomonidan rasmiy saytga yuborilishi uchun to'lov qilishingiz kerak:\n1. Oilalilar (ajrashganlar ham) uchun - 150 000 so'm\n2. Bo'ydoq/yolg'izlar uchun 100 000 so'm",
        "Chekni shu xabar bilan birga adminga yuboring: @GC_helper_admin",
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


# tgbot/handlers/application/confirm.py
@router.callback_query(ApplicationForm.confirm, F.data == "confirm_send")
async def confirm_send(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # 1) Applicant ma'lumotlari
    form_data = {
        "full_name": data.get("full_name"),
        "address": data.get("address"),
        "postal_code": data.get("postal_code", ""),
        "email": data.get("email") or "",
        "education_level": data.get("education_level"),
        "marital_status": data.get("marital_status"),
        "children_count": int(data.get("children_count") or 0),
        "phone_number": data.get("phone_number"),
    }

    # 2) Applicant fayllari - TEKSHRISH VA TO'G'RI SAQLASH
    file_paths = {}

    # Passport faylini tekshirish
    passport_file = data.get("passport_file")
    if passport_file and os.path.exists(passport_file):
        file_paths["passport_file"] = passport_file
    else:
        print(f"⚠️ Passport fayli topilmadi: {passport_file}")

    # Photo faylini tekshirish
    photo_file = data.get("photo_file")
    if photo_file and os.path.exists(photo_file):
        file_paths["photo_file"] = photo_file
    else:
        print(f"⚠️ Photo fayli topilmadi: {photo_file}")
        # Agar photo_file state da bo'sh bo'lsa, lekin fayl mavjud bo'lishi mumkin
        # Qo'shimcha tekshirishlar
        if "photo" in data and data["photo"] and os.path.exists(data["photo"]):
            file_paths["photo_file"] = data["photo"]
            print(f"✅ Photo fayli 'photo' kaliti ostida topildi: {data['photo']}")

    # Inline tugmalarni o'chirish
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    # 3) Applicant yaratish
    status, body, applicant_id = await post_applicant(form_data, file_paths)

    if status in (200, 201) and applicant_id:
        # 4) Dependentslarni yaratish
        errors = []
        for dep in data.get("dependents", []):
            if not isinstance(dep, dict):
                continue

            # Dependent ma'lumotlari
            dep_data = {
                "full_name": dep.get("full_name"),
                "status": dep.get("status"),
            }

            # Dependent fayllari
            dep_files = {}
            if dep.get("passport_file") and os.path.exists(dep.get("passport_file")):
                dep_files["passport_file"] = dep.get("passport_file")
            if dep.get("photo_file") and os.path.exists(dep.get("photo_file")):
                dep_files["photo_file"] = dep.get("photo_file")

            # Dependentni yaratish
            d_status, d_body = await post_dependent(dep_data, applicant_id, dep_files)
            if d_status not in (200, 201):
                errors.append({
                    "dependent": dep_data.get("full_name"),
                    "status": d_status,
                    "body": d_body,
                })

        if not errors:
            await callback.message.answer("✅ Arizangiz va barcha oila a'zolari muvaffaqiyatli yuborildi.")
            await state.clear()
        else:
            error_text = "✅ Applicant yaratildi, ammo ba'zi oila a'zolari yuborishda xatoliklar:\n"
            for e in errors:
                error_text += f"- {e['dependent']}: {e['status']} {e['body']}\n"

            await callback.message.answer(error_text)
    else:
        # Xatolikni qayta ishlash
        error_msg = f"❌ Applicant yuborishda xatolik: {status}\n"

        if isinstance(body, dict):
            for key, value in body.items():
                error_msg += f"{key}: {value}\n"
        else:
            error_msg += str(body)

        await callback.message.answer(error_msg[:1000])

    await callback.answer()