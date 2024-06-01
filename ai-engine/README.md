## AI Engine

The ALPR AI Engine component leverages AI models to detect and recognize license plates. It uses a two-stage engine based on Jetson Inference, where the first stage detects the license plate using an SSD model, and the second stage performs Optical Character Recognition (OCR) using a ResNet model. The results are then sent to the MQTT databus for further processing.



## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
  - [Generating Certificates](#generating-certificates)
- [License](#license)

## Overview <a id='overview'></a>

The ALPR AI Engine component is designed to run on NVIDIA Jetson devices, utilizing the Jetson Inference library for efficient AI processing. It connects to the MQTT databus to send recognized license plates for further processing.

## Features <a id='features'></a>
 - License plate detection using SSD model
 - OCR using ResNet model
 - Secure communication with MQTT databus
 - Efficient AI processing (up to **40 FPS**) on NVIDIA Jetson Nano devices

## Setup Instructions <a id='setup-instructions'></a>

### Prepare models (optional)
he models used for license plate detection and OCR are included in the `engine/models` directory. However, you can update or replace these models with custom ones as needed.

### Configuration

1. Update the configuration in the main script or create a JSON configuration file for the MQTT settings and certificate paths.

```python
config = {
    'broker': 'databus',
    'port': 8883,
    'client_id': 'ai-engine',
    'tls_ca_cert': './certs/ca.crt',
    'tls_certfile': './certs/databus-ai-engine.crt',
    'tls_keyfile': './certs/databus-ai-engine.key',
}
```
2. Set up the MQTT message publishing:

The AI Inference component publishes recognized license plates to the MQTT topic `alpr/ramp/req`.

### Generating Certificates  <a id='generating-certificates'></a>

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

This project is licensed under the terms specified in the [LICENSE](../LICENSE) file.
