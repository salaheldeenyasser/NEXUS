import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULT_SETTINGS = {
    "min_required": 1,
    "admin_pass": "1234",
    "device_pin": "0000",
    "mute": False
}

def get_settings():
    if not os.path.exists(SETTINGS_FILE):
        update_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

    with open(SETTINGS_FILE, "r") as f:
        data = json.load(f)

    # Ensure all required keys exist
    for key in DEFAULT_SETTINGS:
        if key not in data:
            data[key] = DEFAULT_SETTINGS[key]

    return data

def update_settings(new_settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(new_settings, f, indent=2)
