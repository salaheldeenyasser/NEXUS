from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from core.user_profile import update_user_by_id, load_all_user_profiles
from deepface_scripts.training_pipeline import add_new_user

router = APIRouter()

class RoleUpdate(BaseModel):
    role: str

class UserProfileCreate(BaseModel):
    name: str
    role: str
    fingerprint_position: str | None = None

@router.post("/add")
async def add_user(profile: UserProfileCreate):
    # Placeholder admin check (replace with actual auth logic)
    # if not is_admin_request():
    #     raise HTTPException(status_code=403, detail="Admin access required")
    user_id = add_new_user(profile.name, profile.role, profile.fingerprint_position)
    if user_id:
        return {"user_id": user_id, "message": f"User {profile.name} added successfully"}
    raise HTTPException(status_code=500, detail="Failed to add user")

@router.put("/update/{user_id}")
def update_user_role(user_id: str, payload: RoleUpdate):
    success = update_user_by_id(user_id, payload.dict())
    if not success:
        raise HTTPException(status_code=400, detail="Cannot demote the last admin.")
    return {"status": "success", "message": f"Role updated to {payload.role}"}

@router.get("/users/", response_model=List[dict])
def get_all_users():
    return load_all_user_profiles()

@router.get("/profiles", response_model=List[dict])
def get_profiles():
    return [u.to_dict() for u in load_all_user_profiles()]