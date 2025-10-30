import json
import time
import paho.mqtt.client as mqtt
from hardware.aggregator import update_input, log_event
import re

BROKER = "localhost"
MATCH_TOPIC = "door/fingerprint"
COMMAND_TOPIC = "door/cmd"

# Store responses
list_response = None
enroll_response = None
last_list_response_time = 0
LIST_RESPONSE_COOLDOWN = 0.5  # Ignore duplicates within 0.5s

last_enroll_id = None
last_enroll_message_time = 0
ENROLL_MESSAGE_COOLDOWN = 0.5  # Ignore duplicate enroll messages within 0.5s

client = None

def init_mqtt_client(broker="localhost", port=1883, timeout=60):
    global client
    if client is not None and client.is_connected():
        return True
    client = mqtt.Client(client_id=f"fp_input_{int(time.time())}")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    try:
        client.connect(broker, port, timeout)
        client.loop_start()
        start_time = time.time()
        while not client.is_connected() and time.time() - start_time < 5:
            time.sleep(0.1)
        if client.is_connected():
            log_event("MQTT client initialized")
            return True
        else:
            log_event("[ERROR] MQTT connection timeout")
            client.loop_stop()
            client = None
            return False
    except Exception as e:
        log_event("[ERROR] Initial MQTT connect failed", str(e))
        client = None
        return False

def decode_command(payload_str):
    """Parse raw MQTT string into a structured dictionary."""
    try:
        # Try JSON for compatibility
        try:
            return json.loads(payload_str)
        except json.JSONDecodeError:
            pass

        payload_str = payload_str.strip()
        fp_id = None
        match = re.search(r"ID #?(\d+)", payload_str)
        if match:
            fp_id = int(match.group(1))

        # Sensor status
        if payload_str == "Sensor ready":
            return {"action": "sensor_status", "status": "ready"}
        if payload_str == "Sensor error":
            return {"action": "sensor_status", "status": "error"}

        # Matching
        if payload_str == "No match found":
            return {"match": False}
        match = re.match(r"Fingerprint ID: #(\d+)", payload_str)
        if match:
            return {"match": True, "fp_id": int(match.group(1))}

        # Enrollment
        if payload_str == "Invalid ID: Must be between 1 and 127":
            return {"action": "enroll", "status": "failed", "error": "Invalid ID", "fp_id": None}
        if "already in use" in payload_str:
            return {"action": "enroll", "status": "failed", "error": "ID in use", "fp_id": fp_id}
        if any(x in payload_str for x in ["Enroll success", "Enrollment successful", "Fingerprint model created"]):
            return {"action": "enroll", "status": "success", "fp_id": fp_id or last_enroll_id}
        if any(x in payload_str for x in [
            "Enroll failed", "Scan 1 failed after max retries", "Scan 2 failed after max retries",
            "Timeout waiting for finger", "Timeout waiting for finger removal", "Fingerprints do not match"
        ]):
            return {"action": "enroll", "status": "failed", "error": "Scan failed", "fp_id": fp_id}
        if "Image too messy" in payload_str:
            return {"action": "enroll", "status": "failed", "error": "Image too messy", "fp_id": fp_id}
        match = re.match(r"Image conversion failed: Error (\d+)", payload_str)
        if match:
            return {"action": "enroll", "status": "failed", "error": f"Image conversion error {match.group(1)}", "fp_id": fp_id}
        match = re.match(r"Model creation failed: Error (\d+)", payload_str)
        if match:
            return {"action": "enroll", "status": "failed", "error": f"Model creation error {match.group(1)}", "fp_id": fp_id}
        match = re.match(r"Failed to store fingerprint: Error (\d+)", payload_str)
        if match:
            return {"action": "enroll", "status": "failed", "error": f"Store error {match.group(1)}", "fp_id": fp_id}
        match = re.match(r"Retry scan (\d): (\d) attempts remaining", payload_str)
        if match:
            return {"action": "enroll", "message": payload_str, "fp_id": fp_id, "scan_number": int(match.group(1)), "attempts_remaining": int(match.group(2))}

        # Intermediate enrollment steps
        if any(x in payload_str for x in [
            "Starting enrollment", "Place finger for first scan", "Place same finger for second scan",
            "Scan 1 successful", "Scan 2 successful", "Could not identify features"
        ]):
            return {"action": "enroll", "message": payload_str, "fp_id": fp_id}

        # Deleting
        match = re.match(r"Deleted ID (\d+)", payload_str)
        if match:
            return {"action": "delete", "fp_id": int(match.group(1)), "status": "success"}
        match = re.match(r"Failed to delete ID (\d+)", payload_str)
        if match:
            return {"action": "delete", "fp_id": int(match.group(1)), "status": "failed", "error": "Deletion failed"}

        # Listing
        if payload_str == "No enrolled fingerprints":
            return {"action": "list", "positions": []}
        match = re.match(r"Enrolled IDs: ([\d,\s]+)", payload_str)
        if match:
            positions = [int(x) for x in match.group(1).split(",") if x.strip().isdigit()]
            return {"action": "list", "positions": positions}

        # Delete all
        if payload_str == "All fingerprints deleted":
            return {"action": "delete_all", "status": "success"}

        log_event("Unrecognized payload", payload_str)
        return None
    except Exception as e:
        log_event("[ERROR] Failed to decode payload", str(e))
        return None
        
# --------------- MQTT EVENT HANDLERS ---------------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log_event("Connected to MQTT broker")
        client.subscribe(MATCH_TOPIC)
        log_event(f"Subscribed to topics: {MATCH_TOPIC}")
    else:
        log_event("Failed to connect, return code", rc)

def on_disconnect(client, userdata, rc):
    log_event("Disconnected from MQTT broker, reconnecting...")
    try_reconnect(client)

def try_reconnect(client):
    while True:
        try:
            client.reconnect()
            break
        except:
            log_event("Reconnect failed, retrying in 2s")
            time.sleep(2)

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages."""
    global list_response, enroll_response, last_list_response_time, last_enroll_message_time
    try:
        payload_str = msg.payload.decode('utf-8', errors='ignore')
        log_event(f"Raw MQTT message on {msg.topic}", payload_str)
        
        try:
            payload = decode_command(payload_str)
            if not payload or not isinstance(payload, dict):
                return
        except Exception as e:
            log_event("[ERROR] Failed to decode payload", str(e))
            return
        
        # Handle sensor status
        if "action" in payload and payload["action"] == "sensor_status":
            log_event(f"Sensor status: {payload['status']}")
        
        # Handle match
        elif "match" in payload:
            if payload["match"]:
                log_event(f"Fingerprint matched: ID #{payload['fp_id']}")
                update_input("fingerprint_result", payload)
            else:
                log_event("No fingerprint match found")
        
        # Handle list
        elif "action" in payload and payload["action"] == "list" and "positions" in payload:
            current_time = time.time()
            if current_time - last_list_response_time < LIST_RESPONSE_COOLDOWN:
                log_event("Ignoring duplicate list response", payload["positions"])
                return
            last_list_response_time = current_time
            list_response = payload["positions"]
            log_event("Received FP list", list_response)
        
        # Handle enrollment
        elif "action" in payload and payload["action"] == "enroll":
            current_time = time.time()
            if "message" in payload and current_time - last_enroll_message_time < ENROLL_MESSAGE_COOLDOWN:
                log_event("Ignoring duplicate enroll message", payload.get('message'))
                return
            last_enroll_message_time = current_time
            if "status" in payload:
                enroll_response = payload
                if payload["status"] == "success":
                    log_event(f"Enrollment successful for ID #{payload.get('fp_id')}")
                else:
                    log_event(f"Enroll failed: {payload.get('error', 'Unknown error')}")
            else:
                log_event(f"Enroll step: {payload.get('message', payload_str)}")
        
        # Handle delete
        elif "action" in payload and payload["action"] == "delete" and "fp_id" in payload:
            status = "success" if payload["status"] == "success" else "failed"
            log_event(f"Delete ID #{payload['fp_id']} {status}")
        
        # Handle delete all
        elif "action" in payload and payload["action"] == "delete_all":
            log_event("All fingerprints deleted")
    
    except Exception as e:
        log_event("[ERROR] Failed to process FP message", str(e))
        
# --------------- COMMAND PUBLISHING API ---------------

def send_enroll_command(fp_id):
    global enroll_response, last_enroll_id
    last_enroll_id = fp_id
    if client is None:
        init_mqtt_client()
    if client is None:
        log_event("[ERROR] MQTT client initialization failed")
        return False
    enroll_response = None
    command = f"enroll/{fp_id}"
    client.publish(COMMAND_TOPIC, f"enroll/{fp_id}")
    log_event("Sent enroll command", command)
    
    timeout = 30  # Reduced timeout
    start_time = time.time()
    while enroll_response is None and time.time() - start_time < timeout:
        client.loop(0.1)
        time.sleep(0.01)
    if enroll_response is None:
        log_event("[ERROR] No enroll response received")
        return False
    return enroll_response.get("status") == "success"


def send_delete_command(fp_id):
    if client is None:
        init_mqtt_client()
    if client is None:
        log_event("[ERROR] MQTT client initialization failed")
        return
    command = f"delete/{fp_id}"
    client.publish(COMMAND_TOPIC, f"delete/{fp_id}")
    log_event("Sent delete command", command)

def send_list_command():
    global list_response, last_list_response_time
    if client is None:
        init_mqtt_client()
    if client is None:
        log_event("[ERROR] MQTT client initialization failed")
        return []
    list_response = None
    last_list_response_time = 0
    command = "list"
    client.publish(COMMAND_TOPIC, "list")
    log_event("Sent list command", command)
    
    timeout = 15
    start_time = time.time()
    while list_response is None and time.time() - start_time < timeout:
        client.loop(0.1)
        time.sleep(0.01)
    if list_response is None:
        log_event("[ERROR] No list response received")
        return []
    log_event("Returning FP list", list_response)
    return list_response

def send_delete_all_command():
    if client is None:
        init_mqtt_client()
    if client is None:
        log_event("[ERROR] MQTT client initialization failed")
        return
    command = "delete/all"
    client.publish(COMMAND_TOPIC, "delete/all")
    log_event("Sent delete all command", command)

if __name__ == "__main__":
    init_mqtt_client()
    if client is not None:
        try:
            client.loop_forever()
        except Exception as e:
            log_event("[ERROR] MQTT Fingerprint loop crashed", str(e))