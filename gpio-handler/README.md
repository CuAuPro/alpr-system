# GPIO Handler

The GPIO Handler is a component of the Automatic License Plate Recognition System (ALPR System) designed to interface
with GPIO pins on a Jetson Nano. It listens for MQTT messages to control hardware components such as ramps.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
    - [Generating Certificates](#generating-certificates)
- [License](#license)

## Overview <a id='overview'></a>

The GPIO Handler subscribes to specific MQTT topics and controls GPIO pins on a Jetson Nano based on the received
messages. It uses SSL/TLS certificates to secure the communication with the MQTT broker.

## Features <a id='features'></a>

- Subscribes to MQTT topics to control GPIO pins.
- Configurable via JSON configuration files.
- Secure communication with the MQTT broker (Databus) using SSL/TLS.

## Setup Instructions <a id='setup-instructions'></a>

### Configuration

Configuration of the GPIO Handler is done using a YAML file or environment variables. The configuration file must be
placed in the same directory as the executable and named `config.yaml`. The following is an example configuration file:

```yaml
# MQTT client configuration
mqtt:
  broker: "tcp://localhost:1883"
  clientId: "gpio-handler" # Required. Must be unique on the MQTT broker
  auth: # Optional. Leave empty if no authentication is required
    username: ""
    password: ""
  tls: # Optional. Leave empty if no TLS is required
    enabled: false
    ca: ""
    cert: ""
    key: ""

# GPIO configuration for gate control
gate:
  # Closing settings
  close:
    inverse: true # Optional. Invert the output signal
    pin: 17 # Required. GPIO pin number
  # Opening settings
  open:
    inverse: false # Optional. Invert the output signal
    pin: 18 # Required. GPIO pin number

# Logging configuration (optional)
logging:
  level: "info" # Log level: "debug", "info", "warn", "error", "fatal"
```

### Generating Certificates <a id='generating-certificates'></a>

To secure the MQTT communication, you need to generate SSL/TLS certificates. You can use the `mqtt-cryptogen` tool
available at [CuAuPro/mqtt-cryptogen](https://github.com/CuAuPro/mqtt-cryptogen).

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

This project is licensed under the terms specified in the [LICENSE](../LICENSE) file.

