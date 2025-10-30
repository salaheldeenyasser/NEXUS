import json
import time
import pygame
import paho.mqtt.client as mqtt
from hardware.aggregator import update_input, log_event

pygame.mixer.init()
BROKER = "localhost"
TOPIC = "door/keypad"
buffer = []

# Key ID to digit/symbol mapping
KEY_MAPPING = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "*",
    "11": "0",
    "12": "#"
}

def map_key_id(key_id):
    """Translate key ID to digit or symbol."""
    return KEY_MAPPING.get(key_id, None)

# --------------- MQTT EVENT HANDLERS ---------------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log_event("Connected to MQTT broker")
        client.subscribe(TOPIC)
        log_event(f"Subscribed to topic: {TOPIC}")
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
    global buffer
    try:
        key_id = msg.payload.decode().strip()
        log_event("Received keypad key ID", key_id)

        # Map key ID to digit/symbol
        mapped_value = map_key_id(key_id)
        if mapped_value is None:
            log_event("Invalid keypad key ID, resetting buffer")
            buffer.clear()
            return

        buffer.append(mapped_value)
        pygame.mixer.Sound("/home/salah/doorLockGui/hardware/Sounds/Key_press.wav").play()
        log_event("Mapped keypad input", mapped_value)

        if len(buffer) == 4:
            pin_code = "".join(buffer)
            log_event("Complete PIN received", pin_code)
            update_input("pin_result", pin_code)
            buffer.clear()
        elif len(buffer) > 4:
            log_event("Buffer overflow, resetting")
            buffer.clear()
        time.sleep(0.5)

    except Exception as e:
        log_event("[ERROR] Failed to process keypad input", str(e))
        buffer.clear()

# --------------- CLIENT INITIALIZATION ---------------

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

try:
    client.connect(BROKER, 1883, 60)
except Exception as e:
    log_event("[ERROR] Initial MQTT connect failed", str(e))
    try_reconnect(client)

try:
    client.loop_forever()
except Exception as e:
    log_event("[ERROR] MQTT Keypad loop crashed", str(e))