import os
import json
import httpx
from config import API_BASE_URL

async def post_applicant(data: dict, files: dict = None):
    dependents_raw = data.get("dependents", [])

    # 🔁 FLATTEN qilingan form-data
    form_data = {
        "full_name": data["full_name"],
        "email": data["email"],
        "education_level": data["education_level"],
        "postal_code": data["postal_code"],
        "address": data["address"],
        "marital_status": data["marital_status"],
        "children_count": str(data.get("children_count", 0)),
        "phone_number": data["phone_number"],
    }

    # 🔁 dependents flatten
    for idx, dep in enumerate(dependents_raw):
        form_data[f"dependents[{idx}].full_name"] = dep["full_name"]
        form_data[f"dependents[{idx}].status"] = dep["status"]

    files_payload = {}

    if files:
        path = files.get("passport_file")
        if path and os.path.exists(path):
            files_payload["passport_file"] = open(path, "rb")
        path = files.get("photo_file")
        if path and os.path.exists(path):
            files_payload["photo"] = open(path, "rb")

    # 🔁 dependents uchun fayllar
    for idx, dep in enumerate(dependents_raw):
        key_base = f"dependents[{idx}]"
        path = dep.get("passport_file")
        if path and os.path.exists(path):
            files_payload[f"{key_base}.passport_file"] = open(path, "rb")
        path = dep.get("photo_file")
        if path and os.path.exists(path):
            files_payload[f"{key_base}.photo"] = open(path, "rb")

    async with httpx.AsyncClient() as client:
        print("====== POSTING FLATTENED DATA ======")
        for key, value in form_data.items():
            print(f"{key}: {value}")
        print("====== FILES TO SEND =====")
        for key in files_payload:
            print(f"{key}: file attached")
        print("==========================")

        response = await client.post(API_BASE_URL, data=form_data, files=files_payload)

        for f in files_payload.values():
            f.close()

        return response