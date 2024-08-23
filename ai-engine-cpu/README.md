## AI Engine CPU

The ALPR AI Engine component leverages AI models to detect and recognize license plates. It uses a two-stage engine where the first stage detects the license plate using an SSD model, and the second stage performs Optical Character Recognition (OCR) using a ResNet model. The results are then sent to the MQTT databus for further processing.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
    - [Generating Certificates](#generating-certificates)
- [License](#license)

## Overview <a id='overview'></a>

The ALPR AI Engine component is designed to run on CPU-based systems, utilizing efficient AI processing techniques. It connects to the MQTT databus to send recognized license plates for further processing.

## Features <a id='features'></a>

- License plate detection using SSD model
- OCR using ResNet model
- Secure communication with MQTT databus
- Efficient AI processing

## Setup Instructions <a id='setup-instructions'></a>

### Prepare models (optional)

The models used for license plate detection and OCR are included in the `engine/models` directory. However, you can
update or replace these models with custom ones as needed.

### Configuration

1. Create `config.yaml` file inside `./ai-engine/`:

  ```yaml
  # MQTT client configuration
  mqtt:
    broker: "databus"
    port: 8883
    clientId: "ai-engine" # Required. Must be unique on the MQTT broker
    auth: # Optional. Leave empty if no authentication is required
      username: ""
      password: ""
    tls: # Optional. Leave empty if no TLS is required
      enabled: true
      ca: "./certs/ca.crt"
      cert: "./certs/databus-ai-engine.crt"
      key: "./certs/databus-ai-engine.key"

  # AI inference configuration
  engine:
    network: "ssd-mobilenet-v2"
    model: "./engine/models/model-detect.onnx"
    class_labels: "./engine/models/labels-detect.txt"
    input_blob: "input_0"
    output_cvg: "scores"
    output_bbox: "boxes"
    width: 1920
    height: 1080
    threshold: 0.5
    ocr_model: "./engine/models/model-ocr.trt"
    max_retries: 5

  # Camera configuration
  camera:
    - id: 1
      input_stream: "rtsp://192.168.0.15:554/user=admin&password=&channel=1&stream=0.sdp?" # URL of the first camera stream
      output_stream: "rtsp://@:8554/stream" # URL of the first camera output stream

  # Logging configuration (optional)
  logging:
    level: "info" # Log level: "debug", "info", "warn", "error", "fatal"
    print_to_stdout: False
    log_in_file: True
  ```

2. Set up the MQTT message publishing:

The AI Inference component publishes recognized license plates to the MQTT topic `alpr/ramp/req`.

### Generating Certificates  <a id='generating-certificates'></a>

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
