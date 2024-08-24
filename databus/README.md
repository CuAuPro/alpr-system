# Databus

This component of the ALPR System handles the MQTT communication for real-time data transfer between various parts of the system. The databus is secured using SSL/TLS certificates.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Generating Certificates](#generating-certificates)
- [License](#license)

## Overview  <a id='overview'></a>

The MQTT databus enables real-time communication between the different components of the ALPR System, such as the backend server, AI Engine, and GPIO handler. It uses SSL/TLS certificates to ensure secure communication.


## Setup Instructions <a id='setup-instructions'></a>

### Generating Certificates <a id='generating-certificates'></a>

To secure the MQTT communication, you need to generate SSL/TLS certificates. You can use the `mqtt-cryptogen` tool available at [CuAuPro/mqtt-cryptogen](https://github.com/CuAuPro/mqtt-cryptogen).

1. Clone the `mqtt-cryptogen` repository:

```bash
git clone https://github.com/CuAuPro/mqtt-cryptogen.git
```

2. Follow the instructions in the cloned repository, using the configuration files provided in `config-certs/`:

```bash
python ./mqtt-cryptogen/gen_root_cert.py -p ./databus/config-certs/root_cert_req.json
```

```bash
python ./mqtt-cryptogen/gen_client_cert.py -p ./databus/config-certs/client_cert_req.json 
```

```bash
python ./mqtt-cryptogen/extract_pkcs12_certs.py -p ./databus/config-certs/extract_pkcs12_req.json
```

Then copy certificates to each components' volume:

```bash
cp -r ./generated-alpr-cert/databus-broker/* ./databus/certs/
cp -r ./generated-alpr-cert/databus-backend/* ./backend/certs/databus/
cp -r ./generated-alpr-cert/databus-gpio-handler/* ./gpio-handler/certs/
cp -r ./generated-alpr-cert/databus-ai-engine/* ./ai-engine/certs/
cp -r ./generated-alpr-cert/databus-ai-engine/* ./ai-engine-cpu/certs/
```

3. Setup `mosquitto.conf`.

4. Setup (if desired) `acl.conf`.

## License <a id='license'></a>

This project is licensed under the terms specified in the [LICENSE](../LICENSE) file.

