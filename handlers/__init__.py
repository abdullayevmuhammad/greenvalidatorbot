# handlers/__init__.py
from .application import register_application_handlers
from .start import router as start_router  # ✅ yangi

def register_handlers(dp):
    dp.include_router(start_router)              # avval umumiy menyu
    register_application_handlers(dp)            # keyin application FSM routerlari
