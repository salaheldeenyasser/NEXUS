import time
import threading
import requests
import pygame
from collections import deque
from hardware.UnlockDoor import api_open_door


# Session holds the current biometric input results
session = {
    "pin_result": None,
    "face_result": None,
    "fingerprint_result": None
}

pygame.mixer.init()
TIMEOUT = 200
timeout_thread = None
timeout_lock = threading.Lock()

# In-memory log storage for GUI (last 100 logs)
recent_logs = deque(maxlen=100)

def log_event(event, data=None, gui_keywords=False):
    """Log event to file, terminal, and in-memory for GUI."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    message = f"[{timestamp}] {event} {data or ''}".strip()
    # Save to file
    try:
        with open('/tmp/doorlock.log', 'a') as f:
            f.write(message + '\n')
    except Exception as e:
        print(f"[ERROR] Failed to write log: {e}")
    # Save to memory
    recent_logs.append((message, gui_keywords))
    # Print to terminal
    print(message)

def get_recent_logs():
    """Return recent logs filtered for GUI."""
    return [log for log, gui in recent_logs if gui]

def clear_session():
    global session
    log_event("Clearing session", gui_keywords=True)
    session = {
        "pin_result": None,
        "face_result": None,
        "fingerprint_result": None
    }

def post_with_retry(url, json, retries=3, delay=1):
    for attempt in range(retries):
        try:
            response = requests.post(url, json=json, timeout=5)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            log_event(f"[ERROR] Attempt {attempt+1} failed", str(e), gui_keywords=True)
            time.sleep(delay)
    log_event("[ERROR] All retries failed.", gui_keywords=True)
    return None

def session_complete():
    return sum([
        bool(session["pin_result"]),
        bool(session["face_result"] and session["face_result"].get("match")),
        bool(session["fingerprint_result"] and session["fingerprint_result"].get("match"))
    ])

def handle_timeout():
    time.sleep(TIMEOUT)
    with timeout_lock:
        clear_session()

def start_timeout():
    global timeout_thread
    with timeout_lock:
        if timeout_thread is None or not timeout_thread.is_alive():
            timeout_thread = threading.Thread(target=handle_timeout)
            timeout_thread.start()
            log_event("Started session timeout", gui_keywords=True)

def update_input(input_type, value):
    global session
    session[input_type] = value
    log_event(f"Updated session with {input_type}", value, gui_keywords=True)
    pygame.mixer.Sound("/home/salah/doorLockGui/hardware/Sounds/success.wav").play()
    start_timeout()

    if session_complete() >= get_required_inputs():
        payload = {
            "mode": "user",
            "pin": session["pin_result"] or "",
            "admin_pass": "",
            "face_result": session["face_result"] or {},
            "fingerprint_result": session["fingerprint_result"] or {}
        }
        response = post_with_retry("http://localhost:8000/access/", json=payload)
        if response:
            result = response.json()
            log_event("Access attempt sent", result, gui_keywords=True)
            
            if result.get("access_granted") == True:
                log_event(f"[SUCCESS] ", "Access granted, opening door now", gui_keywords=True)
                pygame.mixer.Sound("/home/salah/doorLockGui/hardware/Sounds/door_open.wav").play()
                api_open_door()
            else:
                log_event("[ERROR]", "Access Rejected", gui_keywords=True)
                pygame.mixer.Sound("/home/salah/doorLockGui/hardware/Sounds/failure.wav").play()
        clear_session()

def get_required_inputs():
    try:
        settings = requests.get("http://localhost:8000/admin/settings").json()
        return settings.get("min_required", 2)
    except Exception as e:
        log_event("[ERROR] Failed to fetch settings", str(e), gui_keywords=True)
        return 2