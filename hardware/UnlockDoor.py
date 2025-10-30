import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time

# MQTT settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "door/cmd"

# GPIO config
BUTTON_PIN = 18
GPIO_INITIALIZED = False

# MQTT client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def setup_gpio():
    """Ensure GPIO18 is set up only once."""
    global GPIO_INITIALIZED
    if not GPIO_INITIALIZED:
        if not GPIO.getmode():
            GPIO.setmode(GPIO.BCM)
        try:
            GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO_INITIALIZED = True
        except RuntimeError:
            pass  # Pin likely already set elsewhere

def setup_interrupt():
    """Setup event detection if not already added."""
    if not GPIO.event_detected(BUTTON_PIN):
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=on_button_press, bouncetime=200)

def on_button_press(channel):
    print("Button KEY1 pressed, sending MQTT command: unlock")
    client.publish(MQTT_TOPIC, "unlock")

def api_open_door():
    client.publish(MQTT_TOPIC, "unlock")

# Only set up loop if run directly
if __name__ == "__main__":
    try:
        setup_gpio()
        setup_interrupt()
        print("Monitoring KEY1 on GPIO18...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()
        client.disconnect()
