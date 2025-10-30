#!/usr/bin/env python3
import time
import paho.mqtt.client as mqtt
from hardware.aggregator import log_event
import pygame

pygame.mixer.init()
BROKER = "localhost"
BELL_TOPIC = "door/bell"
COOLDOWN = 1.0  # Seconds between sound plays
last_play_time = 0.0

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log_event("Connected to MQTT broker for bell")
        client.subscribe(BELL_TOPIC)
        log_event(f"Subscribed to topic: {BELL_TOPIC}")
    else:
        log_event(f"Failed to connect to MQTT, return code {rc}")

def on_disconnect(client, userdata, rc):
    log_event("Disconnected from MQTT broker, reconnecting...")
    try_reconnect(client)

def try_reconnect(client):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            client.reconnect()
            log_event("Reconnect successful")
            return
        except Exception as e:
            log_event(f"Reconnect attempt {attempt + 1} failed: {str(e)}")
            time.sleep(2)
    log_event("[ERROR] Reconnect failed after retries")

def on_message(client, userdata, msg):
    global last_play_time
    try:
        payload = msg.payload.decode()
        log_event(f"Received bell message: {payload}")
        if payload == "Bell pressed":
            current_time = time.time()
            if current_time - last_play_time >= COOLDOWN:
                log_event("Notification sent to APP")
                pygame.mixer.Sound("/home/salah/doorLockGui/hardware/Sounds/ding.wav").play()
                last_play_time = current_time
                log_event("Played bell sound")
            else:
                log_event("Bell sound skipped due to cooldown")
    except Exception as e:
        log_event(f"[ERROR] Failed to process bell message: {str(e)}")

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

try:
    client.connect(BROKER, 1883, 60)
except Exception as e:
    log_event(f"[ERROR] Initial MQTT connect failed: {str(e)}")
    try_reconnect(client)

# Start MQTT loop
log_event("Waiting for bell trigger")

try:
    client.loop_forever()
except Exception as e:
    log_event(f"[ERROR] MQTT Bell loop crashed: {str(e)}")