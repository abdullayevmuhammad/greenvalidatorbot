# utils/api.py
import os
import re
import httpx
import mimetypes
from urllib.parse import urlencode, unquote

from config import API_APPLICANTS_URL, API_TOKEN  # ✅ faqat configdan

def _auth_headers():
    h = {}
    if API_TOKEN:
        h["Authorization"] = f"Token {API_TOKEN}"  # JWT bo'lsa: f"Bearer {API_TOKEN}"
    return h

# ---- Fayl tekshiruvlari (ruxsat etilgan turlar) ----
ALLOWED = {
    "application/pdf":  {"ext": "pdf", "magic": b"%PDF"},
    "image/png":        {"ext": "png", "magic": b"\x89PNG\r\n\x1a\n"},
    "image/jpeg":       {"ext": "jpg", "magic": b"\xFF\xD8\xFF"},
}
REDIRECT_CODES = (301, 302, 303, 307, 308)
_cd_filename_re = re.compile(r'filename\*?=(?:UTF-8\'\')?"?([^\";]+)"?', re.I)

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


async def post_applicant(data: dict):
    """
    Oddiy JSON POST so'rovi
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if API_TOKEN:
        headers["Authorization"] = f"Token {API_TOKEN}"



    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                API_APPLICANTS_URL,
                json=data,
                headers=headers
            )
            return response

    except Exception as e:
        print(f"POST so'rovida xatolik: {e}")
        # Xatolik yuz berganda ham Response object qaytarishimiz kerak
        return httpx.Response(500, content=str(e))


async def post_applicant_with_files(data: dict, file_paths: dict):
    """
    data -> oddiy maydonlar (string, int, ...)
    file_paths -> {"passport_file": "passport.pdf", "photo": "photo.jpg"}
    """
    # JSON emas, faqat auth header!
    headers = _auth_headers()

    files = {}
    for field, path in file_paths.items():
        if path and os.path.exists(path):
            mime, _ = mimetypes.guess_type(path)
            files[field] = (
                os.path.basename(path),
                open(path, "rb"),
                mime or "application/octet-stream"
            )

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            API_APPLICANTS_URL,
            data=data,     # oddiy fieldlar
            files=files,   # fayllar
            headers=headers  # ❌ bu yerda Content-Type qo‘ymaslik kerak
        )

    for f in files.values():
        f[1].close()

    return response



# ----------------- EXISTS BY PHONE -----------------
async def phone_exists(phone: str) -> tuple[int, bool | None]:
    """
    Natija:
      (200, True)  -> ro'yxatda bor
      (200, False) -> ro'yxatda yo'q
      (401/403, None) -> ruxsat/avtorizatsiya muammosi
      (boshqa status, None) -> boshqa xatolik
    """
    qs = urlencode({"phone": phone})
    url = f"{API_APPLICANTS_URL}/exists/by-phone/?{qs}"

    # Redirectni kuzatmaymiz — login sahifasini aniqlash uchun
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
        try:
            resp = await client.get(url, headers=_auth_headers())
        except httpx.HTTPError as e:
            print(f"[phone_exists] network error: {e}")
            return 503, None  # tarmoq muammosi

    if resp.status_code in REDIRECT_CODES:
        # odatda login — avtorizatsiya kerak
        print(f"[phone_exists] redirect -> treat as 401/login")
        return 401, None

    if resp.status_code == 200:
        try:
            data = resp.json()
        except ValueError:
            print("[phone_exists] bad json:", resp.text[:200])
            return 502, None
        return 200, (data.get("exists") is True)

    if resp.status_code in (401, 403, 404, 500, 502, 503):
        print(f"[phone_exists] status={resp.status_code} body={resp.text[:200]}")
        return resp.status_code, None

    return resp.status_code, None  # boshqa xatolik yoki noto'g'ri status kodi

# ----------------- CONFIRMATION BY PHONE (GET FILE) -----------------
async def get_confirmation_by_phone(phone: str):
    """
    200: (200, bytes, filename)
    404: (404, None, None)  -> abonent ro'yxatda, lekin fayl hali joylanmagan
    401/403: (401/403, None, None)
    boshqa: (status, None, None)
    """
    qs  = urlencode({"phone": phone})
    url = f"{API_APPLICANTS_URL}/confirmation/by-phone/?{qs}"

    headers = {
        **_auth_headers(),
        "Accept": "application/pdf, image/png, image/jpeg, application/octet-stream",
    }

    # Redirectni kuzatmaymiz: login/HTML'ni fayl deb qabul qilmaslik uchun
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
    """HTML javobni tozalash"""
    if not text or '<' not in text:
        return text

    import re
    # HTML teglarni olib tashlash
    clean_text = re.sub('<[^<]+?>', '', text)
    # HTML entity larni decode qilish
    clean_text = clean_text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    clean_text = clean_text.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")

    return clean_text.strip()
