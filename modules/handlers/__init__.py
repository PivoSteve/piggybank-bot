from aiogram import Router
from .start import router as start_router
from .bank import router as bank_router


router = Router()
router.include_router(start_router)
router.include_router(bank_router)