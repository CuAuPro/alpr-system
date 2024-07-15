# Backend

This directory contains the backend code for the Automatic License Plate Recognition System Management. It is built with Node.js, Express, and SQLite.

## Features

- User authentication with JWT
- Data management with SQLite
- API documentation with Swagger

## Setup Instructions

### Prerequisites

- Node.js
- SQLite


### Swagger API Documentation

The Swagger API documentation for the backend is defined in the `swagger.yaml` file located in the `src/routes` directory. 

| ![](/docs/img/backend-swagger.jpeg) |
|:--:| 
| Dashboard. |

To ensure the correctness of the Swagger API specification, run the following command:

```bash
npx @redocly/cli lint ./src/routes/swagger.yaml
```

To generate TypeScript types from the Swagger API specification, navigate to the `src/routes` directory and run:
```bash
npx openapi-typescript swagger.yaml -o schema.d.ts
```

This will generate TypeScript types in a `schema.d.ts` file based on the Swagger API specification.


### HTTPS Certificates
Generate self-signed certificates for development purposes. For production, use certificates from a trusted Certificate Authority (CA).

Use OpenSSL to generate a self-signed certificate:

```bash
mkdir -p certs/https & cd certs/https
openssl req -nodes -new -x509 -keyout key.pem -out cert.pem -days 3650
```

Then copy certificates to docker volume folder:

```bash
cp cert.pem /var/opt/docker/alpr-system/backend/certs/https/
cp key.pem /var/opt/docker/alpr-system/backend/certs/https/

cp cert.pem /var/opt/docker/alpr-system/frontend/certs/https/
cp key.pem /var/opt/docker/alpr-system/frontend/certs/https/
```


### Installation

1. Install dependencies:

```bash
npm install
```

2. Build the project:

```bash
npm run build
```



## Database Initialization

You have two options to initialize the database:

### Manual Initialization

1. Open SQLite.


2. Run the following SQL commands:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    role TEXT NOT NULL
);

-- Create lp_whitelist table
CREATE TABLE IF NOT EXISTS lp_whitelist (
    id TEXT PRIMARY KEY UNIQUE,
    licensePlate TEXT NOT NULL,
    validFrom DATE NOT NULL,
    validTo DATE NOT NULL
);

-- Create statistics table
CREATE TABLE IF NOT EXISTS statistics (
    id TEXT PRIMARY KEY UNIQUE,
    licensePlate TEXT NOT NULL,
    passDate DATE NOT NULL,
    FOREIGN KEY (id) REFERENCES lp_whitelist(id)
);

-- Create statistics table
CREATE TABLE IF NOT EXISTS lp_whitelist_archive (
    id TEXT PRIMARY KEY UNIQUE,
    licensePlate TEXT NOT NULL,
    validFrom DATE NOT NULL,
    validTo DATE NOT NULL
);

-- Add admin user with hashed password
INSERT INTO users (username, password, firstName, lastName, role)
VALUES ('admin', '$2b$10$icCT4/cxiaAHepb62Cbi9ORYQRJuhKlfKWGkAE6Ia5gZMD5STS.ZW', 'Admin', '', 'admin');
```


### Automatic Initialization

Run the provided initialization script:

```bash
./init-db.sh
```

Copy database file to `database/`.


## Environment Variables

Create an `dev.env` file in the `backend/env` directory with the following contents:

```bash
NODEJS="DEVEL"
PORT=443
JWT_SECRET=your_jwt_secret
```

Create an `prod.env` file in the `backend/env` directory with the following contents:

```bash
NODEJS="PROD"
PORT=443
JWT_SECRET=your_jwt_secret
```


## License

This project is licensed under the terms specified in the [LICENSE](../LICENSE) file.
