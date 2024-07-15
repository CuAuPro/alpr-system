import RPi.GPIO as GPIO

import json
import logging
import threading
from typing import Dict, Any

from logger.logger import init_logger
from engine.mqtt import MQTTEngine
from engine.utils import load_config

class RampController:
    """
    Class to control a ramp gate using GPIO and communicate via MQTT.

    Attributes:
        config (dict): Configuration dictionary.
        ramp_is_open (bool): Flag indicating if the ramp is open.
        ignore_new_requests (bool): Flag indicating whether to ignore new requests.
        ramp_open_timer (threading.Timer): Timer for ramp open duration.
        ramp_ignore_timer (threading.Timer): Timer for ignoring new requests duration.
        mqtt_engine (MQTTEngine): Instance of MQTTEngine for MQTT communication.
        OPEN_PIN (int): GPIO pin number for opening the ramp gate.
        CLOSE_PIN (int): GPIO pin number for closing the ramp gate.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the RampController.

        Args:
            config (dict): Configuration dictionary containing necessary parameters.
        """
        self.config = config
        self.ramp_is_open = False
        self.ignore_new_requests = False
        self.ramp_open_timer = None
        self.ramp_ignore_timer = None
        self.init_gpio()
        self.init_mqtt()

    def init_gpio(self) -> None:
        """
        Initialize GPIO pins based on configuration.
        """
        try:
            self.OPEN_PIN = self.config['gate']['open']['pin']
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.OPEN_PIN, GPIO.OUT, initial=GPIO.HIGH if self.config['gate']['open']['inverse'] else GPIO.LOW)
            if 'close' in self.config['gate'] and 'pin' in self.config['gate']['close']:
                self.CLOSE_PIN = self.config['gate']['close']['pin']
                GPIO.setup(self.CLOSE_PIN, GPIO.OUT, initial=GPIO.LOW if self.config['gate']['close']['inverse'] else GPIO.HIGH)
        except Exception as e:
            logging.error(f"Error initializing GPIO: {e}")
            raise

    def init_mqtt(self) -> None:
        """
        Initialize MQTT connection and subscriptions.
        """
        try:
            mqtt_config = {
                'broker': self.config['mqtt']['broker'],
                'port': self.config['mqtt']['port'],
                'clientId': self.config['mqtt']['clientId'],
                'auth': {
                    'username': self.config['mqtt']['auth']['username'],
                    'password': self.config['mqtt']['auth']['password']
                },
                'tls': {
                    'ca': self.config['mqtt']['tls']['ca'],
                    'cert': self.config['mqtt']['tls']['cert'],
                    'key': self.config['mqtt']['tls']['key']
                }
            }
            self.mqtt_engine = MQTTEngine(mqtt_config)
            self.mqtt_engine.client.tls_insecure_set(True)  # Consider removing in production for secure connections
            self.mqtt_engine.connect()
            self.mqtt_engine.subscribe("alpr/ramp/cmd")
            self.mqtt_engine.client.on_message = self.handle_mqtt
        except Exception as e:
            logging.error(f"Error initializing MQTT: {e}")
            raise

    def handle_mqtt(self, client: Any, userdata: Any, message: Any) -> None:
        """
        Handle incoming MQTT messages.

        Args:
            client (Any): MQTT client instance.
            userdata (Any): MQTT user data.
            message (Any): MQTT message object.
        """
        try:
            topic = message.topic
            data = json.loads(message.payload)
            logging.debug(f"Received MQTT message: {data}")

            if topic == "alpr/ramp/cmd":
                if data["value"] == 1:
                    if self.ramp_is_open or self.ignore_new_requests:
                        logging.debug("Ramp is currently open or new requests are being ignored, ignoring request.")
                        return
                    self.open_ramp()

                    if self.ramp_open_timer:
                        self.ramp_open_timer.cancel()
                    if self.ramp_ignore_timer:
                        self.ramp_ignore_timer.cancel()

                    open_duration = self.config['gate']['open']['duration']
                    self.ramp_open_timer = threading.Timer(open_duration, self.send_ramp_close_command)
                    self.ramp_open_timer.start()

                    ignore_duration = self.config['gate']['ignore_duration']
                    self.ramp_ignore_timer = threading.Timer(ignore_duration, self.stop_ignoring_requests)
                    self.ramp_ignore_timer.start()

                elif data["value"] == 0:
                    self.close_ramp()

                else:
                    logging.error("Invalid command value for ramp!")
            else:
                logging.debug(f"Unknown MQTT topic: {topic}")
        except Exception as e:
            logging.error(f"Exception at handle_mqtt: {e}")
            mqtt_message = {
                "error": "Exception in handle_mqtt",
                "message": str(e)
            }
            self.mqtt_engine.publish(mqtt_message, "alpr/gpio-handler/error")

    def open_ramp(self) -> None:
        """
        Open the ramp gate.
        """
        try:
            GPIO.output(self.OPEN_PIN, GPIO.HIGH if not self.config['gate']['open']['inverse'] else GPIO.LOW)
            logging.debug("Ramp opened")
            self.ramp_is_open = True
            self.ignore_new_requests = True

        except Exception as e:
            logging.error(f"Exception in open_ramp: {e}")
            mqtt_message = {
                "error": "Exception in open_ramp",
                "message": str(e)
            }
            self.mqtt_engine.publish(mqtt_message, "alpr/gpio-handler/error")

    def close_ramp(self) -> None:
        """
        Close the ramp gate.
        """
        try:
            GPIO.output(self.OPEN_PIN, GPIO.LOW if not self.config['gate']['open']['inverse'] else GPIO.HIGH)
            logging.debug("Ramp closed")
            self.ramp_is_open = False
        except Exception as e:
            logging.error(f"Exception in close_ramp: {e}")
            mqtt_message = {
                "error": "Exception in close_ramp",
                "message": str(e)
            }
            self.mqtt_engine.publish(mqtt_message, "alpr/gpio-handler/error")

    def send_ramp_close_command(self) -> None:
        """
        Send a command to close the ramp gate via MQTT.
        """
        try:
            mqtt_message = {
                "value": 0
            }
            self.mqtt_engine.publish(mqtt_message, "alpr/ramp/cmd")
            logging.debug("Ramp close command sent")
        except Exception as e:
            logging.error(f"Exception in send_ramp_close_command: {e}")
            mqtt_message = {
                "error": "Exception in send_ramp_close_command",
                "message": str(e)
            }
            self.mqtt_engine.publish(mqtt_message, "alpr/gpio-handler/error")

    def stop_ignoring_requests(self) -> None:
        """
        Stop ignoring new requests after a certain duration.
        """
        try:
            logging.debug("Stopping to ignore new requests")
            self.ignore_new_requests = False
        except Exception as e:
            logging.error(f"Exception in stop_ignoring_requests: {e}")
            mqtt_message = {
                "error": "Exception in stop_ignoring_requests",
                "message": str(e)
            }
            self.mqtt_engine.publish(mqtt_message, "alpr/gpio-handler/error")

    def start(self) -> None:
        """
        Start the MQTT client's loop to listen for messages.
        """
        try:
            self.mqtt_engine.client.loop_forever()
        except KeyboardInterrupt:
            logging.error("Keyboard interrupt detected, exiting...")
        finally:
            self.mqtt_engine.disconnect()
            GPIO.cleanup()

if __name__ == "__main__":
    try:
        # Load configuration
        config = load_config('config.yaml')

        # Map logging level string to numerical constant
        log_level = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warn": logging.WARNING,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "fatal": logging.FATAL,
            "critical": logging.CRITICAL
        }.get(config['logging']['level'].lower(), logging.INFO)  # Default to INFO if level is not recognized

        # Initialize logger
        init_logger(logging_level=log_level, 
                    print_to_stdout=config['logging']['print_to_stdout'], 
                    log_in_file=config['logging']['log_in_file'])

        # Create RampController instance
        ramp_controller = RampController(config)
        ramp_controller.start()

    except Exception as e:
        logging.error(f"Error in main: {e}")
        mqtt_message = {
            "error": "Exception in main",
            "message": str(e)
        }
        print("MQTT Engine not initialized.")
