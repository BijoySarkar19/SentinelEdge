from fastapi import APIRouter
from app.api.v1.endpoints import auth, cameras, incidents, analytics, search, health, websocket

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
