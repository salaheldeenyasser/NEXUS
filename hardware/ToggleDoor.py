import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time

# MQTT settings
MQTT_BROKER = "localhost"  # Raspberry Pi’s IP or your broker
MQTT_PORT = 1883
MQTT_TOPIC = "door/cmd"

# GPIO settings
BUTTON_PIN = 24  # BCM24 (KEY3 on MPI3201)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Active-low button

# MQTT client setup
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def on_button_press(channel):
    print("Button KEY3 pressed, sending MQTT command: toggle")
    client.publish(MQTT_TOPIC, "toggle")  # Sends 'toggle' to open solenoid

# Interrupt for button press (falling edge for active-low)
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=on_button_press, bouncetime=200)

try:
    print("Monitoring KEY3 on GPIO24...")
    while True:
        time.sleep(1)  # Keep script running
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
    client.disconnect()
