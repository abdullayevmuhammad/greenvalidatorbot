# tgbot/handlers/applcation/__init__.py
from .full_name import router as full_name_router
from .passport import router as passport_router
from .photo import router as photo_router
from .phone import router as phone_router
from .email import router as email_router
from .addres import router as address_router
from .postal_code import router as postal_code_router
from .education_level import router as education_router
from .marital_status import router as marital_status_router
from .wife_full_name import router as wife_full_name_router
from .wife_passport import router as wife_passport_router
from .wife_photo import router as wife_photo_router
from .children_count import router as children_count_router
from .children_photo  import router as child_photo_router

# ✅ Yangi bolalar (farzandlar) uchun handlerlar:
from .child_full_name import router as child_full_name_router
from .child_passport import router as child_passport_router
from .confirm import router as confirm_router

from .get_code_by_phone import router as get_code_by_phone_router

routers = [
    full_name_router,
    passport_router,
    photo_router,
    phone_router,
    email_router,
    address_router,
    postal_code_router,
    education_router,
    marital_status_router,
    wife_full_name_router,
    wife_passport_router,
    wife_photo_router,
    children_count_router,
    child_full_name_router,   # ✅ Farzand ismi
    child_photo_router,
    child_passport_router,
    confirm_router,   # ✅ Farzand hujjati
    get_code_by_phone_router,
]

def register_application_handlers(dp):
    for router in routers:
        dp.include_router(router)
