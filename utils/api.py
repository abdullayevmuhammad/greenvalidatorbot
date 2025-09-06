# tgbot/utils/api.py
import os
import re
import mimetypes
import httpx
from urllib.parse import urlencode, unquote
import json

from config import API_APPLICANTS_URL, API_TOKEN, BASE_URL



# allowed content magic (for file downloads)
ALLOWED = {
    "application/pdf":  {"ext": "pdf", "magic": b"%PDF"},
    "image/png":        {"ext": "png", "magic": b"\x89PNG\r\n\x1a\n"},
    "image/jpeg":       {"ext": "jpg", "magic": b"\xFF\xD8\xFF"},
}
REDIRECT_CODES = (301, 302, 303, 307, 308)
_cd_filename_re = re.compile(r'filename\*?=(?:UTF-8\'\')?"?([^\";]+)"?', re.I)


def _auth_headers():
    h = {}
    if API_TOKEN:
        h["Authorization"] = f"Token {API_TOKEN}"
    return h



def _looks_like_html(data: bytes) -> bool:
    head = (data[:256] or b"").lower()
    return b"<html" in head or b"<!doctype html" in head


def _infer_type_by_magic(data: bytes):
    for ctype, meta in ALLOWED.items():
        if data.startswith(meta["magic"]):
            return ctype, meta["ext"]
    return None, None


def _safe_filename_from_headers(headers, fallback_basename: str, desired_ext: str):
    cd = headers.get("content-disposition") or headers.get("Content-Disposition") or ""
    m = _cd_filename_re.search(cd)
    if m:
        raw = m.group(1)
        try:
            fname = os.path.basename(unquote(raw))
        except Exception:
            fname = os.path.basename(raw)
    else:
        fname = fallback_basename

    root, ext = os.path.splitext(fname)
    ext = (ext or "").lstrip(".").lower()
    if desired_ext and ext != desired_ext:
        fname = f"{root}.{desired_ext}"
    return fname


# Derive dependents URL from applicants URL:
API_ROOT = API_APPLICANTS_URL.rstrip('/').rsplit('/', 1)[0]   # e.g. .../api
DEPENDENTS_URL = f"{API_ROOT}/dependents/"

# tgbot/utils/api.py
async def post_applicant(data: dict, files: dict = None):
    """
    Applicant ma'lumotlarini serverga yuborish
    """
    url = f"{BASE_URL}/applicants/"

    headers = {
        "Accept": "application/json",
    }

    if API_TOKEN:
        headers["Authorization"] = f"Token {API_TOKEN}"

    try:
        # Fayllarni ochib, httpx uchun tayyorlaymiz
        files_dict = {}
        opened_files = []

        if files:
            for key, file_path in files.items():
                if file_path and os.path.exists(file_path):
                    try:
                        file = open(file_path, 'rb')
                        # Serverga mos fayl nomlari
                        if key == "photo_file":
                            files_dict["photo"] = (os.path.basename(file_path), file, 'image/jpeg')
                        elif key == "passport_file":
                            files_dict["passport_file"] = (os.path.basename(file_path), file, 'application/octet-stream')
                        else:
                            files_dict[key] = (os.path.basename(file_path), file, 'application/octet-stream')
                        opened_files.append(file)
                    except Exception as e:
                        print(f"⚠️ Faylni ochishda xatolik: {file_path}, {e}")
                        continue

        async with httpx.AsyncClient(timeout=30.0) as client:
            if files_dict:
                print(f"📤 Fayllar yuborilmoqda: {list(files_dict.keys())}")
                response = await client.post(
                    url,
                    data=data,
                    files=files_dict,
                    headers=headers
                )
            else:
                headers["Content-Type"] = "application/json"
                response = await client.post(
                    url,
                    json=data,
                    headers=headers
                )

            # Fayllarni yopamiz
            for file in opened_files:
                try:
                    file.close()
                except:
                    pass

            # Applicant ID ni olish
            applicant_id = None
            try:
                response_data = response.json()
                if response.status_code in (200, 201) and "id" in response_data:
                    applicant_id = response_data["id"]
            except:
                response_data = response.text

            return response.status_code, response_data, applicant_id

    except Exception as e:
        print(f"Applicant yuborishda xatolik: {e}")
        # Fayllarni yopishni unutmaymiz
        for file in opened_files:
            try:
                file.close()
            except:
                pass
        return 500, {"error": str(e)}, None

async def post_dependent(dependent_data, applicant_id, files=None):
    """
    Yangi dependent yaratish uchun API funksiya
    """
    url = f"{BASE_URL}/dependents/"

    headers = {
        "Accept": "application/json",
    }

    if API_TOKEN:
        headers["Authorization"] = f"Token {API_TOKEN}"

    try:
        # Ma'lumotlarni form-data sifatida yuboramiz
        form_data = {
            "applicant": applicant_id,
            "full_name": dependent_data.get("full_name", ""),
            "status": dependent_data.get("status", "child"),
        }

        # Fayllarni ochib, httpx uchun tayyorlaymiz
        files_dict = {}
        opened_files = []

        if files:
            for key, file_path in files.items():
                if file_path and os.path.exists(file_path):
                    file = open(file_path, 'rb')
                    # Serverdagi field nomlariga mos keladigan keylardan foydalanish
                    if key == "passport_file":
                        files_dict["passport_file"] = (os.path.basename(file_path), file, 'application/octet-stream')
                    elif key == "photo_file":
                        files_dict["photo"] = (os.path.basename(file_path), file, 'image/jpeg')  # photo deb yuborish
                    opened_files.append(file)

        async with httpx.AsyncClient(timeout=30.0) as client:
            if files_dict:
                response = await client.post(
                    url,
                    data=form_data,
                    files=files_dict,
                    headers=headers
                )
            else:
                headers["Content-Type"] = "application/json"
                response = await client.post(
                    url,
                    json=form_data,
                    headers=headers
                )

            # Fayllarni yopamiz
            for file in opened_files:
                file.close()

            return response.status_code, response.json()

    except Exception as e:
        print(f"Dependent yuborishda xatolik: {e}")
        # Fayllarni yopishni unutmaymiz
        for file in opened_files:
            try:
                file.close()
            except:
                pass
        return 500, {"error": str(e)}

# ----------------- phone_exists and get_confirmation_by_phone (keeps previous behavior) -----------------
async def phone_exists(phone: str) -> tuple[int, bool | None]:
    qs = urlencode({"phone": phone})
    url = f"{API_APPLICANTS_URL}/exists/by-phone/?{qs}"

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
        try:
            resp = await client.get(url, headers=_auth_headers())
        except httpx.HTTPError as e:
            print(f"[phone_exists] network error: {e}")
            return 503, None

    if resp.status_code in REDIRECT_CODES:
        return 401, None

    if resp.status_code == 200:
        try:
            data = resp.json()
        except ValueError:
            print("[phone_exists] bad json:", resp.text[:200])
            return 502, None
        return 200, (data.get("exists") is True)

    if resp.status_code in (401, 403, 404, 500, 502, 503):
        return resp.status_code, None

    return resp.status_code, None

async def get_confirmation_by_phone(phone: str):
    url = f"{BASE_URL}/applicants/confirmation/by-phone/"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params={"phone": phone}, headers=_auth_headers())
        except httpx.RequestError as e:
            print(f"[get_confirmation_by_phone] HTTP error: {e}")
            return 500, None

    if resp.status_code != 200:
        return resp.status_code, None

    try:
        data = resp.json()
    except ValueError:
        print("[get_confirmation_by_phone] Bad JSON:", resp.text[:200])
        return 502, None

    return 200, data


def clean_html_response(text: str) -> str:
    if not text or '<' not in text:
        return text

    clean_text = re.sub('<[^<]+?>', '', text)
    clean_text = clean_text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    clean_text = clean_text.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")

    return clean_text.strip()
