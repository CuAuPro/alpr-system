# Automatic License Plate Recognition System (ALPR System)

This project is an Automatic License Plate Recognition (ALPR) system designed for edge devices and optimized for high
performance. It includes an AI Engine for image recognition, a frontend and backend for management, MQTT Databus for
communication, and GPIO interfacing for hardware control.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Setup Instructions](#setup-instructions)
    - [Installation](#installation)
    - [Database Initialization](#database-initialization)
    - [Running the Application](#running-the-application)
- [Components](#components)
    - [Backend](#backend)
    - [Frontend](#frontend)
    - [Databus](#databus)
    - [AI Engine](#ai-engine)
    - [GPIO Handler](#gpio-handler)
- [Environment Variables](#environment-variables)
- [Docker](#docker)
- [License](#license)

## Overview

The ALPR System is designed to provide a comprehensive solution for license plate recognition and management. It
utilizes a combination of AI image recognition, backend APIs, frontend interfaces, and hardware interfacing to deliver a
full-featured ALPR system.

|   ![](/docs/img/system-schematic.jpeg)   |
|:----------------------------------------:| 
| Schematic representation of ALPR System. |

| ![](/docs/img/frontend-dashboard.jpeg) |
|:--------------------------------------:| 
|           ALPR Manager – UI.           |

## Features <a id='features'></a>

- Designed for Edge Devices: Optimized for Jetson Nano.
- High Performance: **AI inference up to 40 FPS**.
- Easy Integration: Seamlessly integrates into existing systems.
- Admin Management: User authentication and management (Angular and Node.js).
- MQTT Communication: Efficient message queuing and data transfer.
- AI-based License Plate Recognition: High accuracy LPR and OCR.
- GPIO Interfacing: Control hardware such as parking ramps.
- Secure: All data is encrypted with HTTPS and Databus over TLS.
- Easy Deployment: Packed as Docker Compose.

## Technology Stack <a id='technology-stack'></a>

- **Backend:** Node.js, Express, SQLite, JWT
- **Frontend:** Angular
- **Databus:** MQTT
- **AI Engine:** Python
- **GPIO Handler:** Python

## Setup Instructions <a id='setup-instructions'></a>

### Installation <a id='installation'></a>

1. Clone the repository:

    ```bash
    git clone https://github.com/CuAuPro/alpr-system.git
    cd alpr-system
    ```

2. Setup backend:

    ```bash
    cd backend
    npm install
    npm run build
    ```

3. Setup frontend:

    ```bash
    cd ../frontend
    npm install
    ng build --configuration=production
    ```

4. Setup MQTT (for additional requirements)

    ```bash
    cd ../databus
    # Follow instructions in mqtt/README.md
    ```

5. Setup Python AI scripts (for additional requirements):

    ```bash
    cd ../ai-engine
    # Follow instructions in ai-engine/README.md
    ```

6. Setup Python GPIO scripts (for additional requirements):

    ```bash
    cd ../gpio-handler
    # Follow instructions in gpio-handler/README.md
    ```

## Components <a id='components'></a>

### Backend <a id='backend'></a>

For detailed instructions on backend setup and usage, refer to `backend/README.md`.

### Frontend <a id='frontend'></a>

For detailed instructions on frontend setup and usage, refer to `frontend/README.md`.

### Databus <a id='databus'></a>

For detailed instructions on Databus setup and usage, refer to `databus/README.md`.

### Python AI <a id='ai-engine'></a>

For detailed instructions on AI setup and usage, refer to `ai-engine/README.md`.

### Python GPIO <a id='gpio-handler'></a>

For detailed instructions on GPIO setup and usage, refer to `gpio-handler/README.md`.

## Environment Variables <a id='environment-variables'></a>

Create a `dev.env` file in the `backend/env` directory with the following contents:

```bash
NODEJS="DEVEL"
PORT=443
JWT_SECRET=your_jwt_secret
```

Create a `prod.env` file in the backend/env directory with the following contents:

```bash
NODEJS="PROD"
PORT=443
JWT_SECRET=your_jwt_secret
```

## Docker Deployment <a id='docker'></a>

Dockerfiles are provided for both the backend and frontend components. You can use Docker Compose to easily build and
run the entire system in containers.

First, please ensure that `docker-compose` is installed. If it is not yet, execute commands:

```bash
sudo apt-get update
sudo apt-get install libhdf5-dev
sudo apt-get install libssl-dev
sudo python3 -m pip install --upgrade pip setuptools

sudo python3 -m pip install docker-compose
```

Docker's `default-runtime` to `nvidia`, so that the NVCC compiler and GPU are available during `docker build` operations.  Add `"default-runtime": "nvidia"` to your `/etc/docker/daemon.json` configuration file before attempting to build the containers (if file doesn't exist, create it):

``` json
{
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    },

    "default-runtime": "nvidia"
}
```

If necessary, install `nvidia-container-runtime`.

```bash
sudo apt-get install nvidia-container-runtime
```

Then restart the Docker service, or reboot your system before proceeding:

```bash
$ sudo systemctl restart docker
```

You can then confirm the changes by looking under `docker info`

```bash
$ sudo docker info | grep 'Default Runtime'
Default Runtime: nvidia
```

You also need to create persistend database file. To create a directory in and set up a volume for the backend alpr.db,
follow these steps:

### Persistent Database File <a id='pesistent-db'></a>
Persistent database file `alpr.db` is placed inside `./backend/database` directory.

### Additional Configuration Files <a id='config-files'></a>
To ensure that volume binds work correctly for additional configuration files, follow these steps:

1. Edit Configuration Files `./gpio-handler/config.yaml` and `./ai-engine/config.yaml`.

### Certificates <a id='certificates'></a>

#### HTTPS <a id='certificates-https'></a>
Please refer to [`backend/README`](backend/README.md). You need to do:

Generate self-signed certificates for development purposes. For production, use certificates from a trusted Certificate Authority (CA).

Use OpenSSL to generate a self-signed certificate:

```bash
openssl req -nodes -new -x509 -keyout key.pem -out cert.pem -days 3650
```

Then copy certificates to docker volume folder:

```bash
sudo mv cert.pem ./backend/certs/https/
sudo mv key.pem ./backend/certs/https/

sudo cp ./backend/certs/https/cert.pem ./frontend/certs/https/
sudo cp ./backend/certs/https/key.pem ./frontend/certs/https/
```


#### Databus <a id='certificates-databus'></a>
For databus communication, refer to specific documentation [`databus/README`](databus/README.md) for certificate generation and configuration. Complete example is provided.

### Starting the Application <a id='starting-app'></a>

To start the application using Docker Compose:

```bash
docker-compose up -d
```

### Building and Running the Application Locally <a id='starting-app-lcoally'></a>

To build the Docker images and run the application locally, use the provided `docker-compose-build.yml` file.
```bash
docker-compose -f docker-compose-build.yml up --build
```

Push images to Docker Hub:

```bash
sudo docker tag alpr-system_backend:latest cuaupro/alpr-system_backend:latest
sudo docker tag alpr-system_frontend:latest cuaupro/alpr-system_frontend:latest
sudo docker tag alpr-system_databus:latest cuaupro/alpr-system_databus:latest
sudo docker tag alpr-system_gpio-handler:latest cuaupro/alpr-system_gpio-handler:latest
sudo docker tag alpr-system_ai-engine:latest cuaupro/alpr-system_ai-engine:latest

sudo docker push cuaupro/alpr-system_backend:latest
sudo docker push cuaupro/alpr-system_frontend:latest
sudo docker push cuaupro/alpr-system_databus:latest
sudo docker push cuaupro/alpr-system_gpio-handler:latest
sudo docker push cuaupro/alpr-system_ai-engine:latest

```

## License <a id='license'></a>

This project is licensed under the terms specified in the [LICENSE](./LICENSE) file.
