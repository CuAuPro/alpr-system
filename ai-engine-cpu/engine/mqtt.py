import paho.mqtt.client as mqtt
import logging
import time
import json
import ssl
import sys

# Constants for reconnection settings
FIRST_RECONNECT_DELAY = (
    1  # Initial delay before the first reconnection attempt (in seconds)
)
RECONNECT_RATE = 1  # Rate at which the reconnection delay increases exponentially
MAX_RECONNECT_COUNT = -1  # Maximum number of reconnection attempts (-1 for infinity)
MAX_RECONNECT_DELAY = 10  # Maximum delay between reconnection attempts (in seconds)

# MQTT Callbacks


def on_connect(client, userdata, flags, rc):
    """
    Callback function invoked when the client successfully connects to the broker.

    Args:
        client: The client instance for this callback.
        userdata: The private user data as set in Client() or userdata_set().
        flags: Response flags sent by the broker.
        rc: The result code returned by the broker.

    Returns:
        None
    """
    logging.info(f"Connected: '{flags}', '{rc}'")


def on_disconnect(client, userdata, rc):
    """
    Callback function invoked when the client disconnects from the broker.

    Args:
        client: The client instance for this callback.
        userdata: The private user data as set in Client() or userdata_set().
        rc: The result code returned by the broker.

    Returns:
        None
    """
    logging.info("Disconnected with result code: {}".format(rc))

    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    if MAX_RECONNECT_COUNT == -1:
        max_reconnect_attempts = float("inf")  # Infinite attempts
    else:
        max_reconnect_attempts = MAX_RECONNECT_COUNT
    # Attempting reconnection with exponential backoff
    while reconnect_count < max_reconnect_attempts:
        logging.info("Reconnecting in {} seconds...".format(reconnect_delay))
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("{}. Reconnect failed. Retrying...".format(err))

        # Exponential backoff for reconnection delay
        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1

    logging.info(
        "Reconnect failed after {} attempts. Exiting...".format(reconnect_count)
    )
    sys.exit(1)  # Exit the program


def on_publish(client, userdata, mid):
    """
    Callback function invoked when a message is successfully published.

    Args:
        client: The client instance for this callback.
        userdata: The private user data as set in Client() or userdata_set().
        mid: The message ID assigned to the published message.

    Returns:
        None
    """
    logging.info(f"Message published with MID: {mid}")


def on_message(client, userdata, message):
    """
    Callback function invoked when a message is received from the broker.

    Args:
        client: The client instance for this callback.
        userdata: The private user data as set in Client() or userdata_set().
        message: An instance of MQTTMessage.

    Returns:
        None
    """
    logging.info(message.topic + " " + str(message.qos) + " " + str(message.payload))


def on_subscribe(client, userdata, mid, granted_qos):
    """
    Callback function invoked when the client successfully subscribes to a topic.

    Args:
        client: The client instance for this callback.
        userdata: The private user data as set in Client() or userdata_set().
        mid: The message ID of the subscribe request.
        granted_qos: A list of QoS levels indicating the granted QoS for each subscription.

    Returns:
        None
    """
    logging.info("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_unsubscribe(client, userdata, mid):
    """
    Callback function invoked when the client successfully unsubscribes from a topic.

    Args:
        client: The client instance for this callback.
        userdata: The private user data as set in Client() or userdata_set().
        mid: The message ID of the unsubscribe request.

    Returns:
        None
    """
    logging.info("Unsubscribed: " + str(mid))


class MQTTEngine:
    """
    Initialize the MQTT Engine.

    Args:
        config (dict): Configuration parameters including broker, port, and client_id.

    Returns:
        None
    """

    def __init__(self, config):
        self.broker = config["broker"]
        self.port = config["port"]
        self.client_id = config["clientId"]
        self.tls_ca_cert = config["tls"]["ca"]
        self.tls_certfile = config["tls"]["cert"]
        self.tls_keyfile = config["tls"]["key"]

        self.client = mqtt.Client(client_id=self.client_id)

        # Set TLS configuration if provided
        if self.tls_ca_cert and self.tls_certfile and self.tls_keyfile:
            self.client.tls_set(
                ca_certs=self.tls_ca_cert,
                certfile=self.tls_certfile,
                keyfile=self.tls_keyfile,
                tls_version=ssl.PROTOCOL_TLS,
            )

        self.client.on_connect = on_connect
        self.client.on_publish = on_publish
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message
        self.client.on_subscribe = on_subscribe
        self.client.on_unsubscribe = on_unsubscribe

    def connect(self):
        """
        Connect to the MQTT broker and start the client's event loop.

        Returns:
        None
        """
        self.client.connect(self.broker, self.port, keepalive=60)
        # self.client.loop_start()

    def disconnect(self):
        """
        Disconnect from the MQTT broker and stop the client's event loop.

        Returns:
        None
        """
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

    def publish(self, data, topic):
        """
        Publish data to an MQTT topic after encoding it as JSON.

        Args:
            data: The data to be published.
            topic (str): The MQTT topic to publish to.

        Returns:
        None
        """
        json_data_str = json.dumps(data)
        self.client.publish(topic, json_data_str)

    def subscribe(self, topic, qos=0):
        """
        Subscribe to an MQTT topic.

        Args:
            topic (str): The MQTT topic to subscribe to.
            qos (int): The Quality of Service level for the subscription. Default is 0.

        Returns:
        None
        """
        self.client.subscribe(topic, qos=qos)

    def unsubscribe(self, topic):
        """
        Unsubscribe from an MQTT topic.

        Args:
            topic (str): The MQTT topic to unsubscribe from.

        Returns:
        None
        """
        self.client.unsubscribe(topic)
