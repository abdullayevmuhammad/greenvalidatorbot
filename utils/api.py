# tgbot/utils/api.py
import os
import re
import mimetypes
import httpx
from urllib.parse import urlencode, unquote
import json

from config import API_APPLICANTS_URL, API_TOKEN

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


# ----------------- POST APPLICANT (with applicant files) -----------------
async def post_applicant(form_data: dict, file_paths: dict):
    """
    Returns: (status_code:int, body: dict|str, applicant_id:int|None)
    form_data: plain fields (strings/ints)
    file_paths: {"passport_file": "/tmp/p.pdf", "photo": "/tmp/photo.jpg"}  (paths optional)
    """
    opened = []
    files = {}

    try:
        # passport_file
        p = file_paths.get("passport_file")
        if p:
            f = open(p, "rb")
            opened.append(f)
            mime, _ = mimetypes.guess_type(p)
            files["passport_file"] = (os.path.basename(p), f, mime or "application/octet-stream")

        # photo (backend field is 'photo')
        ph = file_paths.get("photo") or file_paths.get("photo_file")
        if ph:
            f = open(ph, "rb")
            opened.append(f)
            mime, _ = mimetypes.guess_type(ph)
            files["photo"] = (os.path.basename(ph), f, mime or "application/octet-stream")

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(API_APPLICANTS_URL, data=form_data, files=files, headers=_auth_headers())

        try:
            body = resp.json()
        except Exception:
            body = resp.text

        applicant_id = None
        if resp.status_code in (200, 201) and isinstance(body, dict):
            applicant_id = body.get("id")

        return resp.status_code, body, applicant_id

    except Exception as e:
        return 500, str(e), None

    finally:
        for f in opened:
            try:
                f.close()
            except:
                pass


# ----------------- POST DEPENDENT (with optional files) -----------------
async def post_dependent(dep: dict, applicant_id: int):
    """
    dep: {"full_name":..., "status":..., "passport_file": path_or_None, "photo": path_or_None }
    Returns: (status_code:int, body: dict|str)
    """
    opened = []
    files = {}
    data = {
        "applicant": str(applicant_id),
        "full_name": dep.get("full_name", ""),
        "status": dep.get("status", ""),
    }

    try:
        p = dep.get("passport_file")
        if p:
            f = open(p, "rb")
            opened.append(f)
            mime, _ = mimetypes.guess_type(p)
            files["passport_file"] = (os.path.basename(p), f, mime or "application/octet-stream")

        ph = dep.get("photo") or dep.get("photo_file")
        if ph:
            f = open(ph, "rb")
            opened.append(f)
            mime, _ = mimetypes.guess_type(ph)
            files["photo"] = (os.path.basename(ph), f, mime or "application/octet-stream")

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(DEPENDENTS_URL, data=data, files=files, headers=_auth_headers())

        try:
            body = resp.json()
        except Exception:
            body = resp.text

        return resp.status_code, body

    except Exception as e:
        return 500, str(e)

    finally:
        for f in opened:
            try:
                f.close()
            except:
                pass


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
    qs = urlencode({"phone": phone})
    url = f"{API_APPLICANTS_URL}/confirmation/by-phone/?{qs}"

    headers = {
        **_auth_headers(),
        "Accept": "application/pdf, image/png, image/jpeg, application/octet-stream",
    }

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=False) as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code in REDIRECT_CODES:
        return 401, None, None
    if resp.status_code in (401, 403, 404):
        return resp.status_code, None, None
    if resp.status_code != 200:
        return resp.status_code, None, None

    body = resp.content or b""
    if not body or _looks_like_html(body):
        return 415, None, None

    ctype = (resp.headers.get("content-type") or "").split(";")[0].strip().lower()
    ok = False
    ext = None

    if ctype in ALLOWED:
        ok = body.startswith(ALLOWED[ctype]["magic"])
        ext = ALLOWED[ctype]["ext"] if ok else None

    if not ok:
        inferred, inf_ext = _infer_type_by_magic(body)
        if inferred:
            ctype, ext, ok = inferred, inf_ext, True

    if not ok or not ext:
        return 415, None, None

    filename = _safe_filename_from_headers(
        resp.headers, fallback_basename=f"confirmation_{phone}", desired_ext=ext
    )
    return 200, body, filename


def clean_html_response(text: str) -> str:
    if not text or '<' not in text:
        return text

    clean_text = re.sub('<[^<]+?>', '', text)
    clean_text = clean_text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    clean_text = clean_text.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")

    return clean_text.strip()
