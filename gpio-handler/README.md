# GPIO Hanlder

The GPIO Handler is a component of the Automatic License Plate Recognition System (ALPR System) designed to interface with GPIO pins on a Jetson Nano. It listens for MQTT messages to control hardware components such as ramps.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
  - [Generating Certificates](#generating-certificates)
- [License](#license)

## Overview <a id='overview'></a>

The GPIO Handler subscribes to specific MQTT topics and controls GPIO pins on a Jetson Nano based on the received messages. It uses SSL/TLS certificates to secure the communication with the MQTT broker.

## Features <a id='features'></a>
- Subscribes to MQTT topics to control GPIO pins.
- Configurable via JSON configuration files.
- Secure communication with the MQTT broker (Databus) using SSL/TLS.

## Setup Instructions <a id='setup-instructions'></a>

### Configuration

1. Update the configuration in the main script or create a JSON configuration file for the MQTT settings and certificate paths.

```python
config = {
    'broker': 'databus',
    'port': 8883,
    'client_id': 'gpio-handler',
    'tls_ca_cert': './certs/ca.crt',
    'tls_certfile': './certs/databus-gpio-handler.crt',
    'tls_keyfile': './certs/databus-gpio-handler.key',
}
```
2. Set up the MQTT message handling:
The GPIO Handler listens for messages on the topic `alpr/ramp/cmd` and toggles the GPIO pin based on the message payload.

```python
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
```
### Generating Certificates <a id='generating-certificates'></a>

To secure the MQTT communication, you need to generate SSL/TLS certificates. You can use the `mqtt-cryptogen` tool available at [CuAuPro/mqtt-cryptogen](https://github.com/CuAuPro/mqtt-cryptogen).

1. Clone the `mqtt-cryptogen` repository:

```bash
git clone https://github.com/CuAuPro/mqtt-cryptogen.git
cd mqtt-cryptogen
```

2. Follow the instructions in the cloned repository, using the configuration files provided in `config-certs/`:

```bash
python <path-to-mqtt-cryptogen>/gen_root_cert.py -p <path-to-databus>/config-certs/root_cert_req.json
```

```bash
python <path-to-mqtt-cryptogen>/gen_client_cert.py -p <path-to-databus>/config-certs/client_cert_req.json 
```

```bash
python <path-to-mqtt-cryptogen>/extract_pkcs12_certs.py -p <path-to-databus>/config-certs/extract_pkcs12_req.json
```
3. Configure (if desired) `acl.conf`.


## License <a id='license'></a>

This project is licensed under the MIT License.

