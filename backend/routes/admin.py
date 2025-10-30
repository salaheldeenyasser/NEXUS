from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from utils import settings
from utils.settings import get_settings, update_settings
from core.user_profile import load_all_user_profiles
from core.logic import process_access_attempt
from utils.auth import create_token
from deepface_scripts.embed_utils import load_embeddings
import os
import json

print("Admin router loaded")

router = APIRouter()

# ------------------------------
# Settings endpoints
# ------------------------------

@router.get("/settings")
def get_settings_route():
    return get_settings()

@router.post("/settings")
def update_settings_route(new_settings: dict):
    update_settings(new_settings)
    return {"status": "Settings updated."}

# ------------------------------
# Admin login with biometrics
# ------------------------------

class AdminLoginRequest(BaseModel):
    pin: str
    face_result: dict
    fingerprint_result: dict

@router.post("/login")
def admin_login(payload: AdminLoginRequest = Body(...)):
    settings = get_settings()
    profiles = load_all_user_profiles()
    for admin in profiles:
        if admin.role != "admin":
            continue

        result = process_access_attempt(
            mode="admin",
            pin=payload.pin,
            admin_pass=settings.get("admin_pass"),
            face_result=payload.face_result,
            fingerprint_result=payload.fingerprint_result,
            current_user=admin
        )
        if result["access_granted"]:
            token = create_token(admin.name)
            return {"token": token}

    raise HTTPException(status_code=401, detail="Admin authentication failed.")

# ------------------------------
# Reset user profiles
# ------------------------------

@router.post("/reset")
def system_reset():
    user_file = os.path.join(os.path.dirname(__file__), "..", "utils", "user_profiles.json")
    with open(user_file, "w") as f:
        json.dump([], f)
    return {"status": "System reset successful."}

# ------------------------------
# Change Device PIN
# ------------------------------

@router.post("/change-pin")
def change_pin(new_pin: str = Query(...)):
    if not new_pin.isdigit() or len(new_pin) != 4:
        raise HTTPException(status_code=400, detail="PIN must be 4 digits")
    data = settings.get_settings()
    data["device_pin"] = new_pin
    settings.update_settings(data)
    return {"status": "success", "new_pin": new_pin}

# ------------------
# Get embeddings
# ------------------

@router.get("/api/embeddings")
def get_embeddings():
    embeddings = load_embeddings()
    return {"embeddings": embeddings}

# ------------------
# Get Settings
# ------------------

@router.post("/verify-pin")
def verify_admin_pin(pin: str = Query(...)):
    settings = get_settings()
    return {"success": pin == settings.get("admin_pass")}

# ------------------
# Update Admin PIN
# ------------------

@router.post("/change-admin-pin")
def change_admin_pin(new_pin: str = Query(...)):
    if not new_pin.isdigit() or len(new_pin) != 4:
        raise HTTPException(status_code=400, detail="PIN must be 4 digits")
    data = settings.get_settings()
    data["admin_pass"] = new_pin
    settings.update_settings(data)
    return {"status": "success", "message": "Admin PIN updated successfully"}


# No need to "export" explicitly — just make sure the file has the correct 'router' defined