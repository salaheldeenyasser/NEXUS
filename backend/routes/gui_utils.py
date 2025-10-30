from fastapi import APIRouter
from pydantic import BaseModel, validator
from hardware.fp_input import send_delete_command, send_enroll_command, send_delete_all_command
from hardware.aggregator import log_event
from backend.utils.settings import get_settings, update_settings
from backend.core.user_profile import get_user_by_id, remove_user_by_id, load_all_user_profiles, update_user_by_id
from deepface_scripts.embed_utils import load_embeddings, save_embeddings
from deepface_scripts.training_pipeline import add_new_user, start_face_embedding_extraction
import os
import re
import uuid
import json

# File paths
BASE_DIR = "/home/salah/doorLockGui"
USER_PROFILES_PATH = os.path.join(BASE_DIR, "backend/utils/user_profiles.json")
SETTINGS_PATH = os.path.join(BASE_DIR, "backend/settings.json")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "deepface_scripts/face_embeddings.pkl")

# Valid roles
VALID_ROLES = ["user", "admin"]

# FastAPI router
router = APIRouter()

# Pydantic models for request validation
class UserRequest(BaseModel):
    name: str
    role: str
    apply_face_pipeline: bool = True
    apply_finger_pipeline: bool = True

    @validator("name")
    def validate_name(cls, v):
        """Sanitize name: alphanumeric, spaces, max 50 chars."""
        if not re.match(r'^[a-zA-Z0-9\s]{1,50}$', v):
            raise ValueError("Name must be alphanumeric with spaces, max 50 characters")
        return v.strip()

    @validator("role")
    def validate_role(cls, v):
        """Ensure role is valid and normalize to lowercase."""
        v = v.lower()
        if v not in VALID_ROLES:
            raise ValueError(f"Role must be one of {VALID_ROLES}")
        return v

class UserIdRequest(BaseModel):
    user_id: str

    @validator("user_id")
    def validate_user_id(cls, v):
        """Ensure user_id is a valid UUID4 string."""
        try:
            uuid.UUID(v, version=4)
            return v
        except ValueError:
            raise ValueError("user_id must be a valid UUID4 string")

class UpdateUserRequest(BaseModel):
    name: str | None = None
    role: str | None = None

    @validator("name", pre=True, always=True)
    def validate_name(cls, v):
        """Sanitize name if provided: alphanumeric, spaces, max 50 chars."""
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9\s]{1,50}$', v):
            raise ValueError("Name must be alphanumeric with spaces, max 50 characters")
        return v.strip()

    @validator("role", pre=True, always=True)
    def validate_role(cls, v):
        """Ensure role is valid and normalize to lowercase if provided."""
        if v is None:
            return v
        v = v.lower()
        if v not in VALID_ROLES:
            raise ValueError(f"Role must be one of {VALID_ROLES}")
        return v

class ResetRequest(BaseModel):
    pass  # Empty payload for reset

class CreateUserProfileRequest(BaseModel):
    name: str
    role: str
    fingerprint_position: int | None = None
    face_embeddings: list | None = None

    @validator("name")
    def validate_name(cls, v):
        """Sanitize name: alphanumeric, spaces, max 50 chars."""
        if not re.match(r'^[a-zA-Z0-9\s]{1,50}$', v):
            raise ValueError("Name must be alphanumeric with spaces, max 50 characters")
        return v.strip()

    @validator("role")
    def validate_role(cls, v):
        """Ensure role is valid and normalize to lowercase."""
        v = v.lower()
        if v not in VALID_ROLES:
            raise ValueError(f"Role must be one of {VALID_ROLES}")
        return v

# === Modular Functions ===
def create_user_profile(name: str, role: str) -> str | None:
    try:
        user_id = str(uuid.uuid4())
        success = add_new_user(
            user_id=user_id,
            name=name,
            role=role,
            fp_position=None
        )
        if success:
            log_event("[SUCCESS] Created user profile", f"user_id: {user_id}, name: {name}, role: {role}", gui_keywords=True)
            return user_id
        else:
            log_event("[ERROR] Failed to create user profile", f"name: {name}, role: {role}", gui_keywords=True)
            return None
    except Exception as e:
        log_event("[ERROR] create_user_profile exception", str(e), gui_keywords=True)
        return None

def add_face_embeddings(user_id: str) -> bool:
    try:
        log_event("Starting face embedding extraction", f"user_id: {user_id}", gui_keywords=True)
        embeddings = start_face_embedding_extraction(user_id)
        if not embeddings:
            log_event("[ERROR] Failed to capture face embeddings", f"user_id: {user_id}", gui_keywords=True)
            return False

        all_embeddings = load_embeddings(EMBEDDINGS_PATH)
        for emb in embeddings:
            emb['user_id'] = user_id
        all_embeddings.extend(embeddings)
        save_embeddings(all_embeddings, EMBEDDINGS_PATH)

        log_event("[SUCCESS] Face embeddings saved", f"user_id: {user_id}", gui_keywords=True)
        return True
    except Exception as e:
        log_event("[ERROR] add_face_embeddings exception", str(e), gui_keywords=True)
        return False

def enroll_fingerprint(user_id: str) -> tuple[bool, int | None]:
    try:
        log_event("Starting fingerprint enrollment", f"user_id: {user_id}", gui_keywords=True)
        enrolled = send_list_command()
        if enrolled is None:
            log_event("[ERROR] Fingerprint sensor not responding", gui_keywords=True)
            return False, None

        available_position = next((i for i in range(1, 128) if i not in enrolled), None)
        if available_position is None:
            log_event("[ERROR] No available fingerprint positions", gui_keywords=True)
            return False, None

        success = send_enroll_command(available_position)
        if not success:
            log_event("[ERROR] Failed to enroll fingerprint", f"user_id: {user_id}", gui_keywords=True)
            return False, None

        updated = update_user_by_id(user_id, {"fingerprint_position": available_position})
        if not updated:
            log_event("[ERROR] Failed to update user profile with fingerprint", f"user_id: {user_id}", gui_keywords=True)
            return False, None

        log_event("[SUCCESS] Fingerprint enrolled", f"user_id: {user_id}, position: {available_position}", gui_keywords=True)
        return True, available_position
    except Exception as e:
        log_event("[ERROR] enroll_fingerprint exception", str(e), gui_keywords=True)
        return False, None


# === New API Routes ===
@router.post("/create_basic_user")
async def api_create_basic_user(request: UserRequest):
    user_id = create_user_profile(request.name, request.role)
    if user_id:
        return {"success": True, "user_id": user_id}
    return {"success": False, "error": "Failed to create user"}

@router.post("/add_face")
async def api_add_face(request: UserIdRequest):
    if add_face_embeddings(request.user_id):
        return {"success": True, "message": "Face added successfully"}
    return {"success": False, "error": "Failed to add face"}

@router.post("/add_fingerprint")
async def api_add_fingerprint(request: UserIdRequest):
    success, position = enroll_fingerprint(request.user_id)
    if success:
        return {"success": True, "fingerprint_position": position}
    return {"success": False, "error": "Failed to enroll fingerprint"}

# API Endpoints
@router.post("/add_user")
async def add_new_user_endpoint(request: UserRequest):
    """
    Add a new user with optional face embeddings and fingerprint based on pipeline flags.
    
    Parameters:
        request (UserRequest): JSON payload with name, role, apply_face_pipeline, and apply_finger_pipeline
                              (e.g., {"name": "John Doe", "role": "user", "apply_face_pipeline": false, "apply_finger_pipeline": true}).
    
    Returns:
        dict: {"success": bool, "message": str, "user_id": str}
        user_id is a UUID4 string (e.g., "123e4567-e89b-12d3-a456-426614174000").
        
    Example:
        curl -X POST "http://localhost:8000/gui/add_user" -H "Content-Type: application/json" \
             -d '{"name": "John Doe", "role": "user", "apply_face_pipeline": false, "apply_finger_pipeline": true}'
    """
    try:
        log_event(f"Received add_user request", f"{request.dict()}", gui_keywords=True)
        
        # Initialize variables for face embeddings and fingerprint
        id = str(uuid.uuid4())
        face_embeddings = None
        fingerprint_position = None
        
        # Apply face embedding pipeline if requested
        if request.apply_face_pipeline:
            log_event(f"Starting face embedding extraction for user: {request.name}", gui_keywords=True)
            face_embeddings = start_face_embedding_extraction(id)  # Assumes temp user_id handled internally
            if not face_embeddings:
                log_event("[ERROR] Failed to capture face embeddings", f"name: {request.name}", gui_keywords=True)
                return {"success": False, "error": "Failed to capture face embeddings"}
            log_event(f"[SUCCESS] Captured face embeddings for user: {request.name}", gui_keywords=True)
        
        # Apply fingerprint pipeline if requested
        if request.apply_finger_pipeline:
            log_event(f"Starting fingerprint enrollment for user: {request.name}", gui_keywords=True)
            from hardware.fp_input import send_list_command
            enrolled_fps = send_list_command()
            if enrolled_fps is None:
                log_event("[ERROR] Failed to get fingerprint list", gui_keywords=True)
                return {"success": False, "error": "Failed to communicate with fingerprint sensor"}
            
            # Find next available position
            available_position = None
            for i in range(1, 20):  # Max 127 fingerprints
                if i not in enrolled_fps:
                    available_position = i
                    break
            
            if available_position is None:
                log_event("[ERROR] No available fingerprint positions", gui_keywords=True)
                return {"success": False, "error": "No available fingerprint positions"}
            
            success = send_enroll_command(available_position)
            if success:
                fingerprint_position = available_position
                log_event(f"[SUCCESS] Enrolled fingerprint at position {available_position} for user: {request.name}", gui_keywords=True)
            else:
                log_event(f"[ERROR] Failed to enroll fingerprint for user: {request.name}", gui_keywords=True)
                return {"success": False, "error": "Fingerprint enrollment failed"}
        
        # Add the user with collected data
        user_id = add_new_user(
            user_id = id,
            name=request.name,
            role=request.role,
            fp_position=fingerprint_position
        )
        if user_id:
            # Save face embeddings if any
            if face_embeddings:
                embeddings = load_embeddings(EMBEDDINGS_PATH)
                for emb in face_embeddings:
                    emb['user_id'] = user_id
                embeddings.extend(face_embeddings)
                save_embeddings(embeddings, EMBEDDINGS_PATH)
            
            log_event(f"[SUCCESS] Added user", f"id: {user_id}, name: {request.name}, role: {request.role}, "
                     f"fingerprint_position: {fingerprint_position}, has_embeddings: {bool(face_embeddings)}", gui_keywords=True)
            return {"success": True, "message": "User added successfully", "user_id": user_id}
        else:
            log_event("[ERROR] Failed to add user", f"name: {request.name}, role: {request.role}", gui_keywords=True)
            return {"success": False, "error": "Failed to add new user"}
    except Exception as e:
        log_event("[ERROR] add_new_user error", str(e), gui_keywords=True)
        return {"success": False, "error": str(e)}

@router.post("/retake_face_embeddings")
async def retake_face_embeddings(request: UserIdRequest):
    """
    Delete and retake face embeddings for a user, append to face_embeddings.pkl.
    
    Parameters:
        request (UserIdRequest): JSON payload with user_id (e.g., {"user_id": "123e4567-e89b-12d3-a456-426614174000"}).
    
    Returns:
        dict: {"success": bool, "message": str}
        
    Example:
        curl -X POST "http://localhost:8000/gui/retake_face_embeddings" -H "Content-Type: application/json" \
             -d '{"user_id": "123e4567-e89b-12d3-a456-426614174000"}'
    """
    try:
        user_id = request.user_id
        log_event(f"Retaking face embeddings", f"user_id: {user_id}", gui_keywords=True)
        embeddings = load_embeddings(EMBEDDINGS_PATH)
        embeddings = [emb for emb in embeddings if emb.get('user_id') != user_id]
        
        new_embeddings = start_face_embedding_extraction(user_id)
        if not new_embeddings:
            log_event("[ERROR] Failed to capture embeddings", f"user_id: {user_id}", gui_keywords=True)
            return {"success": False, "error": "Failed to capture new embeddings"}
        
        embeddings.extend(new_embeddings)
        save_embeddings(embeddings, EMBEDDINGS_PATH)
        log_event("[SUCCESS] Retaken embeddings", f"user_id: {user_id}", gui_keywords=True)
        return {"success": True, "message": "Face embeddings retaken successfully"}
    except FileNotFoundError:
        log_event("[ERROR] retake_face_embeddings error", f"face_embeddings.pkl not found for user_id: {user_id}", gui_keywords=True)
        return {"success": False, "error": "Embeddings file not found"}
    except Exception as e:
        log_event("[ERROR] retake_face_embeddings error", f"{str(e)} for user_id: {user_id}", gui_keywords=True)
        return {"success": False, "error": str(e)}

@router.post("/retake_fingerprint")
async def retake_fingerprint(request: UserIdRequest):
    """
    Delete and re-enroll fingerprint for a user.
    
    Parameters:
        request (UserIdRequest): JSON payload with user_id (e.g., {"user_id": "123e4567-e89b-12d3-a456-426614174000"}).
    
    Returns:
        dict: {"success": bool, "message": str}
        
    Example:
        curl -X POST "http://localhost:8000/gui/retake_fingerprint" -H "Content-Type: application/json" \
             -d '{"user_id": "123e4567-e89b-12d3-a456-426614174000"}'
    """
    try:
        user_id = request.user_id
        log_event(f"Retaking fingerprint", f"user_id: {user_id}", gui_keywords=True)
        user = get_user_by_id(user_id)
        if not user or not user.fingerprint_position:
            log_event("[ERROR] User not found or no fingerprint_position", f"user_id: {user_id}", gui_keywords=True)
            return {"success": False, "error": "User not found or no fingerprint ID"}
        
        fp_position = user.fingerprint_position
        send_delete_command(int(fp_position))
        log_event(f"Sent delete command", f"fp_position: {fp_position}, user_id: {user_id}", gui_keywords=True)
        
        success = send_enroll_command(int(fp_position))
        if success:
            log_event("[SUCCESS] Re-enrolled fingerprint", f"user_id: {user_id}, fp_position: {fp_position}", gui_keywords=True)
            return {"success": True, "message": "Fingerprint retaken successfully"}
        else:
            log_event("[ERROR] Failed to re-enroll fingerprint", f"user_id: {user_id}, fp_position: {fp_position}", gui_keywords=True)
            return {"success": False, "error": "Failed to re-enroll fingerprint"}
    except Exception as e:
        log_event("[ERROR] retake_fingerprint error", f"{str(e)} for user_id: {user_id}", gui_keywords=True)
        return {"success": False, "error": str(e)}

@router.post("/delete_user_profile")
async def delete_user_profile(request: UserIdRequest):
    """
    Delete a user's fingerprint, embeddings, and profile.
    
    Parameters:
        request (UserIdRequest): JSON payload with user_id (e.g., {"user_id": "123e4567-e89b-12d3-a456-426614174000"}).
    
    Returns:
        dict: {"success": bool, "message": str}
    
    Note:
        The GUI must prompt for the admin password ("5678") before allowing this action. No server-side authentication is enforced.
        
    Example:
        curl -X POST "http://localhost:8000/gui/delete_user_profile" -H "Content-Type: application/json" \
             -d '{"user_id": "123e4567-e89b-12d3-a456-426614174000"}'
    """
    try:
        user_id = request.user_id
        log_event(f"Deleting user profile", f"user_id: {user_id}", gui_keywords=True)
        
        user = get_user_by_id(user_id)
        if not user:
            log_event("[ERROR] User not found", f"user_id: {user_id}", gui_keywords=True)
            return {"success": False, "error": "User not found"}
        
        # Delete fingerprint if available
        # if user.fingerprint_position is not None:
        #     send_delete_command(int(user.fingerprint_position))
        #     log_event(f"Sent delete command", f"fp_position: {user.fingerprint_position}, user_id: {user_id}", gui_keywords=True)
        
        # Delete face embeddings
        embeddings = load_embeddings(EMBEDDINGS_PATH)
        embeddings = [emb for emb in embeddings if emb.get('user_id') != user_id]
        save_embeddings(embeddings, EMBEDDINGS_PATH)
        
        # Remove profile
        remove_user_by_id(user_id)
        log_event("[SUCCESS] Deleted user profile", f"user_id: {user_id}", gui_keywords=True)
        return {"success": True, "message": "User profile deleted successfully"}
    
    except Exception as e:
        log_event("[ERROR] delete_user_profile error", f"{str(e)} for user_id: {user_id}", gui_keywords=True)
        return {"success": False, "error": str(e)}

@router.post("/update_user")
async def update_user(request: UserIdRequest, update_data: UpdateUserRequest):
    """
    Update a user's name and/or role.
    
    Parameters:
        request (UserIdRequest): JSON payload with user_id (e.g., {"user_id": "123e4567-e89b-12d3-a456-426614174000"}).
        update_data (UpdateUserRequest): JSON payload with name and/or role (e.g., {"name": "Jane Doe", "role": "admin"}).
    
    Returns:
        dict: {"success": bool, "message": str}
    
    Note:
        Cannot demote the last admin to user role.
        
    Example:
        curl -X POST "http://localhost:8000/gui/update_user" -H "Content-Type: application/json" \
             -d '{"user_id": "123e4567-e89b-12d3-a456-426614174000", "name": "Jane Doe", "role": "admin"}'
    """
    try:
        user_id = request.user_id
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        if not update_dict:
            log_event("[ERROR] No updates provided", f"user_id: {user_id}", gui_keywords=True)
            return {"success": False, "error": "No updates provided"}
        
        log_event(f"Updating user", f"user_id: {user_id}, updates: {update_dict}", gui_keywords=True)
        success = update_user_by_id(user_id, update_dict)
        if success:
            log_event("[SUCCESS] Updated user", f"user_id: {user_id}", gui_keywords=True)
            return {"success": True, "message": "User updated successfully"}
        else:
            log_event("[ERROR] Failed to update user", f"Cannot demote last admin, user_id: {user_id}", gui_keywords=True)
            return {"success": False, "error": "Cannot demote last admin"}
    except Exception as e:
        log_event("[ERROR] update_user error", f"{str(e)} for user_id: {user_id}", gui_keywords=True)
        return {"success": False, "error": str(e)}

@router.post("/reset_system")
async def reset_system(request: ResetRequest):
    """
    Reset embeddings, fingerprints, and settings to default.
    
    Parameters:
        request (ResetRequest): Empty JSON payload.
    
    Returns:
        dict: {"success": bool, "message": str}
    
    Note:
        The GUI must prompt for the admin password ("5678") before allowing this action. No server-side authentication is enforced.
        
    Example:
        curl -X POST "http://localhost:8000/gui/reset_system" -H "Content-Type: application/json" \
             -d '{}'
    """
    try:
        log_event("Starting system reset", gui_keywords=True)
        
        # Reset embeddings
        try:
            save_embeddings([], EMBEDDINGS_PATH)
            log_event("Reset all face embeddings", gui_keywords=True)
        except Exception as e:
            log_event("[ERROR] Failed to reset embeddings", str(e), gui_keywords=True)
            raise
        
        # Delete all fingerprints
        send_delete_all_command()
        log_event("Sent delete all command to fingerprint sensor", gui_keywords=True)
        
        # Reset settings
        default_settings = {
            "min_required": 2,
            "admin_pass": "5678",
            "device_pin": "1234",
            "mute": False
        }
        if not (isinstance(default_settings["min_required"], int) and
                isinstance(default_settings["admin_pass"], str) and
                isinstance(default_settings["device_pin"], str) and
                isinstance(default_settings["mute"], bool)):
            log_event("[ERROR] Invalid default settings types", gui_keywords=True)
            return {"success": False, "error": "Invalid default settings types"}
        
        update_settings(default_settings)
        log_event("Reset system settings to default", gui_keywords=True)
        
        # Clear user profiles
        if os.path.exists(USER_PROFILES_PATH):
            with open(USER_PROFILES_PATH, "w") as f:
                json.dump([], f, indent=2)
            log_event("Cleared all user profiles", gui_keywords=True)
        
        log_event("[SUCCESS] System reset successful", gui_keywords=True)
        return {"success": True, "message": "System reset successfully"}
    except Exception as e:
        log_event("[ERROR] reset_system error", str(e), gui_keywords=True)
        return {"success": False, "error": str(e)}

@router.get("/users")
async def get_users():
    """
    Get list of all users from user_profiles.json.
    
    Returns:
        dict: {"success": bool, "message": str, "users": list}
        Each user has user_id as a UUID4 string (e.g., "123e4567-e89b-12d3-a456-426614174000").
        
    Example:
        curl -X GET "http://localhost:8000/gui/users"
    """
    try:
        log_event("Fetching all users", gui_keywords=True)
        profiles = load_all_user_profiles()
        users = [
            {
                "user_id": p.id,
                "name": p.name,
                "role": p.role,
                "fingerprint_position": p.fingerprint_position
            }
            for p in profiles
        ]
        log_event("[SUCCESS] Fetched users", f"count: {len(users)}", gui_keywords=True)
        return {"success": True, "message": "Users fetched successfully", "users": users}
    except Exception as e:
        log_event("[ERROR] get_users error", str(e), gui_keywords=True)
        return {"success": False, "error": str(e)}
    
@router.post("/enroll_fingerprint")
async def enroll_fingerprint_only():
    """
    Enroll a fingerprint and return the position.
    
    Returns:
        dict: {"success": bool, "message": str, "fingerprint_position": int}
    """
    try:
        log_event("Starting fingerprint enrollment", gui_keywords=True)
        
        # Get list of enrolled fingerprints to find next available position
        from hardware.fp_input import send_list_command
        
        enrolled_fps = send_list_command()
        if enrolled_fps is None:
            log_event("[ERROR] Failed to get fingerprint list", gui_keywords=True)
            return {"success": False, "error": "Failed to communicate with fingerprint sensor"}
        
        # Find next available position (1-based)
        available_position = None
        for i in range(1, 128):  # Assuming max 127 fingerprints
            if i not in enrolled_fps:
                available_position = i
                break
        
        if available_position is None:
            log_event("[ERROR] No available fingerprint positions", gui_keywords=True)
            return {"success": False, "error": "No available fingerprint positions"}
        
        # Enroll the fingerprint
        success = send_enroll_command(available_position)
        
        if success:
            log_event(f"[SUCCESS] Fingerprint enrolled at position {available_position}", gui_keywords=True)
            return {
                "success": True, 
                "message": "Fingerprint enrolled successfully",
                "fingerprint_position": available_position
            }
        else:
            log_event(f"[ERROR] Failed to enroll fingerprint at position {available_position}", gui_keywords=True)
            return {"success": False, "error": "Fingerprint enrollment failed"}
            
    except Exception as e:
        log_event(f"[ERROR] enroll_fingerprint error: {str(e)}", gui_keywords=True)
        return {"success": False, "error": str(e)}

@router.post("/capture_face_embeddings")
async def capture_face_embeddings_only():
    """
    Capture face embeddings and return them.
    
    Returns:
        dict: {"success": bool, "message": str, "face_embeddings": list}
    """
    try:
        log_event("Starting face capture", gui_keywords=True)
        
        # Generate a temporary user ID for capturing
        import uuid
        temp_user_id = str(uuid.uuid4())
        
        from deepface_scripts.training_pipeline import capture_and_process_images
        embeddings = capture_and_process_images(temp_user_id)
        
        if embeddings:
            log_event(f"[SUCCESS] Face embeddings captured", gui_keywords=True)
            return {
                "success": True,
                "message": "Face captured successfully",
                "face_embeddings": embeddings
            }
        else:
            log_event("[ERROR] Failed to capture face embeddings", gui_keywords=True)
            return {"success": False, "error": "Failed to capture face"}
            
    except Exception as e:
        log_event(f"[ERROR] capture_face_embeddings error: {str(e)}", gui_keywords=True)
        return {"success": False, "error": str(e)}

@router.post("/create_user_profile")
async def create_user_profile_old(request: CreateUserProfileRequest):
    """
    Create a user profile with existing fingerprint position and face embeddings.
    
    Parameters:
        request: JSON with name, role, fingerprint_position (optional), face_embeddings (optional)
    
    Returns:
        dict: {"success": bool, "message": str, "user_id": str}
    """
    try:
        log_event(f"Creating user profile", f"name: {request.name}, role: {request.role}", gui_keywords=True)
        
        # Generate user ID
        import uuid
        user_id = str(uuid.uuid4())
        
        # Create user profile
        from backend.core.user_profile import create_user_profile as create_profile
        success = create_profile(
            user_id=user_id,
            name=request.name,
            role=request.role,
            fingerprint_position=request.fingerprint_position
        )
        
        if not success:
            log_event("[ERROR] Failed to create user profile", gui_keywords=True)
            return {"success": False, "error": "Failed to create user profile"}
        
        # Save face embeddings if provided
        if request.face_embeddings:
            embeddings = load_embeddings(EMBEDDINGS_PATH)
            # Update user_id in the embeddings
            for embedding in request.face_embeddings:
                embedding['user_id'] = user_id
            embeddings.extend(request.face_embeddings)
            save_embeddings(embeddings, EMBEDDINGS_PATH)
        
        log_event(f"[SUCCESS] Created user profile", f"user_id: {user_id}", gui_keywords=True)
        return {
            "success": True,
            "message": "User profile created successfully",
            "user_id": user_id
        }
        
    except Exception as e:
        log_event(f"[ERROR] create_user_profile error: {str(e)}", gui_keywords=True)
        return {"success": False, "error": str(e)}