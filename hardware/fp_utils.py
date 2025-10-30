try:
    from hardware.fp_input import send_list_command, send_enroll_command
except ImportError as e:
    print(f"Import error in fp_utils: {e}")
    raise

from hardware.aggregator import log_event

def get_smallest_available_position():
    """Find the smallest available fingerprint position (1 to 3000)."""
    try:
        occupied = send_list_command()
        if not isinstance(occupied, list):
            raise ValueError("Invalid positions list")
        
        for i in range(1, 3001):
            if i not in occupied:
                return i
        raise ValueError("No available positions")
    except Exception as e:
        log_event("[ERROR] Failed to get smallest position", str(e))
        return None

def enroll_fingerprint():
    """Enroll a new fingerprint and return the position."""
    try:
        fp_position = get_smallest_available_position()
        if fp_position is None:
            raise ValueError("No available fingerprint position")
        
        log_event(f"Starting enrollment for ID #{fp_position}")
        success = send_enroll_command(fp_position)
        
        if success:
            log_event(f"Enrollment successful for ID #{fp_position}")
            return fp_position
        else:
            raise ValueError("Fingerprint enrollment failed")
    except Exception as e:
        log_event("[ERROR] Failed to enroll fingerprint", str(e))
        return None