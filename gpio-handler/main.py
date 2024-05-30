import RPi.GPIO as GPIO

import json
import logging

from logger.logger import init_logger
from engine.mqtt import MQTTEngine

# Pin Definitions
OUTPUT_PIN = 18  # BCM pin 18, BOARD pin 12

def handle_mqtt(client, userdata, message):
    try:
        topic = message.topic
        data = json.loads(message.payload)
        logging.debug(data)

        if topic == "alpr/ramp/cmd":
            if data["value"] == 1:
                GPIO.output(OUTPUT_PIN, GPIO.HIGH)
            elif data["value"] == 0:
                GPIO.output(OUTPUT_PIN, GPIO.LOW)
            else:
                logging.error("Invalid command for ramp!")
        else:
            logging.debug("Unknown mqtt topic: {}".format(topic))
    except Exception as e:
        logging.error("Exception at handle_mqtt: {}".format(e))
        
if __name__ == "__main__":
    init_logger(logging_level=logging.INFO, print_to_stdout=False, log_in_file=True)

    config = {  'broker': 'databus',
                'port': 8883,
                'client_id': 'gpio-handler',
                'tls_ca_cert': './certs/ca.crt',
                'tls_certfile': './certs/databus-gpio-handler.crt',
                'tls_keyfile': './certs/databus-gpio-handler.key',
             }
    mqtt_engine = MQTTEngine(config)
    mqtt_engine.client.tls_insecure_set(True)
    mqtt_engine.connect()
    mqtt_engine.subscribe("alpr/ramp/cmd")
    mqtt_engine.client.on_message = handle_mqtt
    # Pin Setup:
    GPIO.setmode(GPIO.BCM)  # BCM pin-numbering scheme from Raspberry Pi
    # set pin as an output pin with optional initial state of HIGH
    GPIO.setup(OUTPUT_PIN, GPIO.OUT, initial=GPIO.LOW)
    try:
        mqtt_engine.client.loop_forever()
    except KeyboardInterrupt:
        logging.error("Keyboard interrupt detected, exiting...")
    finally:
        mqtt_engine.disconnect()
        GPIO.cleanup()