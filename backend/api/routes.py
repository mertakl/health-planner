from fastapi import APIRouter

from backend.api.endpoints import plans

router = APIRouter()

# All endpoint routers
router.include_router(plans.router)
