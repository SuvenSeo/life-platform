from fastapi import APIRouter

from app.api.v1.endpoints.internal import router as internal_router
from app.api.v1.endpoints.life import router as life_router
from app.api.v1.endpoints.me import router as me_router

api_router = APIRouter()
api_router.include_router(life_router, prefix="/life", tags=["life"])
api_router.include_router(me_router, prefix="/me", tags=["me"])
api_router.include_router(internal_router, prefix="/internal", tags=["internal"])
