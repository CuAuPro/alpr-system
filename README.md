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

## Docker <a id='docker'></a>

Dockerfiles are provided for both the backend and frontend components. You can use Docker Compose to easily build and
run the entire system in containers.

Docker's `default-runtime` to `nvidia`, so that the NVCC compiler and GPU are available during `docker build` operations.  Add `"default-runtime": "nvidia"` to your `/etc/docker/daemon.json` configuration file before attempting to build the containers:

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

1. Create Directory: Open a terminal and run the following command to create a directory named `alpr-system`
   in `/var/opt/docker/database`:

    ```bash
    sudo mkdir -p /var/opt/docker/alpr-system/database
    ```

2. Copy initialized `alpr.db` to `/var/opt/docker/alpr-system/database`.

3. Set Up Volume: After creating the directory, you can specify a volume for the backend alpr.db in your Docker Compose
   file. Add the following volume configuration under the backend service in your `docker-compose.yml` file:

    ```yaml
    volumes:
      - /var/opt/docker/alpr-system/database:/app/backend/database
    ```

To start the application using Docker Compose:

```bash
docker-compose up --build
```

## License <a id='license'></a>

This project is licensed under the terms specified in the [LICENSE](./LICENSE) file.
