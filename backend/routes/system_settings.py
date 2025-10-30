# routes/system_settings.py
from fastapi import APIRouter
from utils import settings  # Adjust if your utils folder path differs

router = APIRouter()

@router.get("/system-settings")
def get_system_settings():
    return settings.get_settings()

@router.post("/system-settings")
def update_system_settings(new_settings: dict):
    current = settings.get_settings()
    current.update(new_settings)
    settings.update_settings(current)
    return {"status": "success", "updated": new_settings}