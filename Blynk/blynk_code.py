import paho.mqtt.client as mqtt
import threading
import logging
import time
import os
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

def run_flask():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # Suppress Flask's development server logs
    app.run(host='0.0.0.0', port=5000)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_DOOR_LOCK = "door/lock"
MQTT_TOPIC_CMD = "door/cmd"
MQTT_TOPIC_BELL = "door/bell"
MQTT_TOPIC_STATUS = "smartlock/door_status"
MQTT_TOPIC_LOGS = "smartlock/logs"

log_dir = '/home/salah/doorLockGui/Blynk'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(filename=f'{log_dir}/door_logs.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

client = mqtt.Client()
last_lock_state = None
unlock_timer = None

def reset_lock_status():
    global last_lock_state, unlock_timer
    if unlock_timer:
        unlock_timer.cancel()
    client.publish(MQTT_TOPIC_STATUS, "Locked")
    client.publish(MQTT_TOPIC_LOGS, f"{datetime.now()} - Door reset to Locked")
    last_lock_state = "Locked"

def on_connect(client, userdata, flags, rc):
    client.subscribe(MQTT_TOPIC_BELL)
    client.subscribe(MQTT_TOPIC_DOOR_LOCK)
    print("Connected to MQTT Broker")
    try:
        with open(f'{log_dir}/door_logs.txt', 'r') as log_file:
            logs = log_file.readlines()[-10:]
            for log in logs:
                client.publish(MQTT_TOPIC_LOGS, log.strip())
                print(f"Published log to Blynk: {log.strip()}")
    except FileNotFoundError:
        print("No previous logs found")
    client.publish(MQTT_TOPIC_STATUS, "Locked")  # Set default status

def on_message(client, userdata, msg):
    global last_lock_state, unlock_timer
    if msg.topic == MQTT_TOPIC_BELL:
        bell_state = msg.payload.decode()
        if bell_state == "Bell pressed" and (last_lock_state != "Bell Pressed"):
            log_message = "Bell Pressed"
            logging.info(log_message)
            client.publish(MQTT_TOPIC_BELL, "Bell pressed")
            client.publish(MQTT_TOPIC_LOGS, f"{datetime.now()} - {log_message}")
            last_lock_state = "Bell Pressed"
    elif msg.topic == MQTT_TOPIC_DOOR_LOCK:
        lock_state = msg.payload.decode()
        if lock_state == "Unlocked" and lock_state != last_lock_state:
            logging.info(f"Door Lock Status: {lock_state}")
            client.publish(MQTT_TOPIC_STATUS, lock_state)
            client.publish(MQTT_TOPIC_LOGS, f"{datetime.now()} - Door Unlocked")
            last_lock_state = lock_state
            if unlock_timer:
                unlock_timer.cancel()
            unlock_timer = threading.Timer(5.0, reset_lock_status)
            unlock_timer.start()
        elif lock_state in ["Toggled High", "Toggled Low"] and lock_state != last_lock_state:
            logging.info(f"Door Lock Status: {lock_state}")
            client.publish(MQTT_TOPIC_STATUS, lock_state)
            client.publish(MQTT_TOPIC_LOGS, f"{datetime.now()} - {lock_state}")
            last_lock_state = lock_state

def lock_door(command):
    client.publish(MQTT_TOPIC_CMD, command)

client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=lambda: None, daemon=True).start()
    client.loop_forever()