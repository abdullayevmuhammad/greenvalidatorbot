import os

def get_download_path(filename: str) -> str:
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)
    return os.path.join(download_dir, filename)

import os

def safe_filename(file_id: str, file_name: str, max_length: int = 100):
    ext = os.path.splitext(file_name)[1]
    base = f"{file_id}_{os.path.splitext(file_name)[0]}"
    # Kengaytma + "_" joyi ham hisobga olinadi
    limit = max_length - len(ext)
    if len(base) > limit:
        base = base[:limit]
    return f"{base}{ext}"
