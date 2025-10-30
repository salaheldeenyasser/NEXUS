def process_access_attempt(mode, pin=None, admin_pass=None, face_result=None, fingerprint_result=None):
    from utils.settings import get_settings
    settings = get_settings()
    
    # Normal user mode
    score = 0
    if face_result and face_result.get("match"):
        score += 1
    if fingerprint_result and fingerprint_result.get("match"):
        score += 1
    if pin == settings.get("device_pin"):
        score += 1

    passed = score >= settings.get("min_required", 2)
    return {
        "access_granted": passed,
        "matched_user": face_result.get("name") if face_result else None,
        "score": score
    }
