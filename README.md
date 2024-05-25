# Automatic License Plate Recognition System (ALPR System)

This project is an Automatic License Plate Recognition System Management built with Angular for the frontend and Node.js for the backend. It is designed to provide a robust starting point for developing a full-stack application with user authentication, admin management, and other features. The system also includes components for MQTT communication, AI-based image recognition, and GPIO interfacing.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
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

The ALPR System is designed to provide a comprehensive solution for license plate recognition and management. It utilizes a combination of backend APIs, frontend interfaces, AI image recognition, and hardware interfacing to achieve its goals.

## Features <a id='features'></a>

- User authentication and authorization
- Admin management with CRUD operations
- MQTT communication
- AI-based license plate recognition
- GPIO interfacing for hardware control

## Technology Stack <a id='technology-stack'></a>

- **Backend:** Node.js, Express, SQLite, JWT
- **Frontend:** Angular
- **Databus:** MQTT
- **AI Engine:** Python
- **GPIO Handler:** Python

## Setup Instructions <a id='setup-instructions'></a>

### Prerequisites

- Node.js
- Angular CLI
- SQLite
- Docker (optional, for containerized deployment)
- MQTT broker (if using MQTT)
- Python (if using Python scripts)

### Installation <a id='installation'></a>

1. Clone the repository:

```bash
git clone https://github.com/yourusername/alpr-system.git
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

4. Setup MQTT (for additional requirmenets)
```bash

cd ../databus
# Follow instructions in mqtt/README.md
```

5. Setup Python AI scripts (for additional requirmenets):

```bash
cd ../ai-engine
# Follow instructions in ai-engine/README.md
```

6. Setup Python GPIO scripts (for additional requirmenets):

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
For detailed instructions on GPIO setup and usage, refer to gpio-handler/README.md.

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
Dockerfiles are provided for both the backend and frontend components. You can use Docker Compose to easily build and run the entire system in containers.

You also need to create persistend database file. To create a directory in and set up a volume for the backend alpr.db, follow these steps:

1. Create Directory: Open a terminal and run the following command to create a directory named `alpr-system` in `/var/opt/docker/database`:
```bash
sudo mkdir -p /var/opt/docker/alpr-system/database
```

2. Set Up Volume: After creating the directory, you can specify a volume for the backend alpr.db in your Docker Compose file. Add the following volume configuration under the backend service in your `docker-compose.yml` file:
```yaml
volumes:
  - /var/opt/docker/alpr-system/database:/app/backend/database
```


To start the application using Docker Compose:

```bash
docker-compose up --build
```
## License <a id='license'></a>

This project is licensed under the MIT License.

