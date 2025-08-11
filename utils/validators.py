import os

ALLOWED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"]
MAX_FILE_SIZE_MB = 5  # Maksimal ruxsat etilgan fayl hajmi, MB

def validate_file_extension(file_name: str):
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
        raise ValueError("❌ Noto‘g‘ri fayl turi. Faqat .jpg, .jpeg, .png yoki .pdf fayllar ruxsat etiladi.")

def validate_file_size(file_size: int):
    limit = 2 * 1024 * 1024  # 2 MB
    if file_size > limit:
        raise ValueError("❌ Fayl hajmi 2MB dan oshmasligi kerak.")
