import RPi.GPIO as GPIO

import json
import logging

from logger.logger import init_logger
from engine.mqtt import MQTTEngine
from engine.utils import load_config

def handle_mqtt(client, userdata, message):
    try:
        topic = message.topic
        data = json.loads(message.payload)
        logging.debug(f"Received MQTT message: {data}")

        if topic == "alpr/ramp/cmd":
            if data["value"] == 1:
                GPIO.output(OPEN_PIN, GPIO.HIGH if not config['gate']['open']['inverse'] else GPIO.LOW)
            elif data["value"] == 0:
                GPIO.output(OPEN_PIN, GPIO.LOW if not config['gate']['open']['inverse'] else GPIO.HIGH)
            else:
                logging.error("Invalid command value for ramp!")
        else:
            logging.debug(f"Unknown MQTT topic: {topic}")
    except Exception as e:
        logging.error(f"Exception at handle_mqtt: {e}")
        


if __name__ == "__main__":
    # Load configuration
    config = load_config('gpio_config.yaml')

    # Initialize logger
    init_logger(logging_level=config['logging']['level'], 
                print_to_stdout=config['logging']['print_to_stdout'], 
                log_in_file=config['logging']['log_in_file'])
    
    # MQTT configuration
    mqtt_config = {
        'broker': config['mqtt']['broker'],
        'port': config['mqtt']['port'],
        'client_id': config['mqtt']['clientId'],
        'auth': {
            'username': config['mqtt']['auth']['username'],
            'password': config['mqtt']['auth']['password']
        },
        'tls': {
            'ca': config['mqtt']['tls']['ca'],
            'cert': config['mqtt']['tls']['cert'],
            'key': config['mqtt']['tls']['key']
        }
    }
    
    # Initialize GPIO for opening gate
    OPEN_PIN = config['gate']['open']['pin']
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OPEN_PIN, GPIO.OUT, initial=GPIO.LOW if config['gate']['open']['inverse'] else GPIO.HIGH)
    
    # Initialize GPIO for closing gate if defined in config
    if 'close' in config['gate'] and 'pin' in config['gate']['close']:
        CLOSE_PIN = config['gate']['close']['pin']
        GPIO.setup(CLOSE_PIN, GPIO.OUT, initial=GPIO.LOW if config['gate']['close']['inverse'] else GPIO.HIGH)
    
    # Initialize MQTT Engine
    mqtt_engine = MQTTEngine(mqtt_config)
    mqtt_engine.client.tls_insecure_set(True)  # Consider removing this in production for secure connections
    mqtt_engine.connect()
    mqtt_engine.subscribe("alpr/ramp/cmd")
    mqtt_engine.client.on_message = handle_mqtt
    try:
        mqtt_engine.client.loop_forever()
    except KeyboardInterrupt:
        logging.error("Keyboard interrupt detected, exiting...")
    finally:
        mqtt_engine.disconnect()
        GPIO.cleanup()