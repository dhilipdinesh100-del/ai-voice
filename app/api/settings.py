from typing import Dict, Any
from fastapi import APIRouter
from app.schemas.settings import SettingsUpdate
from app.database.repositories.settings_repo import SettingsRepository

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("", response_model=Dict[str, Any])
def get_settings():
    return SettingsRepository.get_all()

@router.patch("", response_model=Dict[str, Any])
def update_settings(payload: SettingsUpdate):
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return SettingsRepository.update(update_data)
