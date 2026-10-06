from fastapi import APIRouter

from app.api.endpoints import sessions, audio, forms, extractions

api_router = APIRouter()

api_router.include_router(forms.router, prefix="/forms", tags=["forms"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(extractions.router, prefix="/extractions", tags=["extractions"])
