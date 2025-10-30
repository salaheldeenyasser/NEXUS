import json
import os
import uuid
from dataclasses import dataclass, asdict

USER_FILE = os.path.join(os.path.dirname(__file__), "..", "utils", "user_profiles.json")

@dataclass
class UserProfile:
    id: str
    name: str
    role: str
    fingerprint_position: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            role=data["role"],
            fingerprint_position=data["fingerprint_position"]
        )

def load_all_user_profiles():
    with open(USER_FILE, "r") as f:
        return [UserProfile.from_dict(item) for item in json.load(f)]

def save_user_profile(profile: UserProfile):
    users = load_all_user_profiles()
    users.append(profile)
    with open(USER_FILE, "w") as f:
        json.dump([u.to_dict() for u in users], f, indent=2)

def get_user_by_id(profile_id: str):
    return next((u for u in load_all_user_profiles() if u.id == profile_id), None)

def remove_user_by_id(profile_id: str):
    users = load_all_user_profiles()
    updated_users = [u for u in users if u.id != profile_id]
    with open(USER_FILE, "w") as f:
        json.dump([u.to_dict() for u in updated_users], f, indent=2)

def update_user_by_id(profile_id: str, updated_data: dict):
    users = load_all_user_profiles()
    updated_users = []
    admin_count = sum(1 for u in users if u.role == "admin")

    for user in users:
        if user.id == profile_id:
            new_role = updated_data.get("role", user.role)
            if user.role == "admin" and new_role == "user" and admin_count == 1:
                return False  # Cannot demote last admin

            for key in ["name", "role", "fingerprint_position"]:
                if key in updated_data:
                    setattr(user, key, updated_data[key])
        updated_users.append(user)

    with open(USER_FILE, "w") as f:
        json.dump([u.to_dict() for u in updated_users], f, indent=2)

    return True