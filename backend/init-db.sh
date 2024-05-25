#!/bin/bash

# Path to your SQLite database file
DATABASE_PATH="alpr.db"

# Delete the existing alpr.db file if it exists
if [ -f "$DATABASE_PATH" ]; then
    echo "Deleting existing alpr.db file..."
    rm "$DATABASE_PATH"
fi

# Hash the admin user's password
HASHED_PASSWORD=$(htpasswd -bnBC 10 "" admin | tr -d ':\n' | sed 's/$2y/$2b/')

# SQLite commands to create tables and add admin user
sqlite3 "$DATABASE_PATH" <<EOF
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
VALUES ('admin', '$HASHED_PASSWORD', 'Admin', 'User', 'admin');
EOF

