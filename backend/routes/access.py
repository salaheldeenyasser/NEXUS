from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from core.logic import process_access_attempt
from utils import settings
from hardware.aggregator import recent_logs

router = APIRouter()

class FaceResult(BaseModel):
    match: Optional[bool] = None
    name: Optional[str] = None

class FingerprintResult(BaseModel):
    match: Optional[bool] = None
    fp_id: Optional[int] = None

class AccessRequest(BaseModel):
    mode: Optional[str] = "user"
    pin: Optional[str] = None
    admin_pass: Optional[str] = None
    face_result: Optional[FaceResult] = None
    fingerprint_result: Optional[FingerprintResult] = None

@router.post("/")
def check_access(data: AccessRequest):
    result = process_access_attempt(
        mode=data.mode,
        pin=data.pin,
        admin_pass=data.admin_pass,
        face_result=data.face_result.dict() if data.face_result else None,
        fingerprint_result=data.fingerprint_result.dict() if data.fingerprint_result else None
    )
    return result

@router.get("/recent-logs")
def get_recent_logs():
    return list(recent_logs)