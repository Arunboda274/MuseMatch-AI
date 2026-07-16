from fastapi import APIRouter

from app.routes.song.core import router as core_router
from app.routes.song.delete import router as delete_router
from app.routes.song.read import router as read_router
from app.routes.song.stream import router as stream_router
from app.routes.song.update import router as update_router


router = APIRouter()

router.include_router(core_router)
router.include_router(read_router)
router.include_router(update_router)
router.include_router(delete_router)
router.include_router(stream_router)


__all__ = ["router"]