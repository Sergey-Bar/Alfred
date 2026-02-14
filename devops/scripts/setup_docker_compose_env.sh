#!/bin/bash

# Script to set up a full local development environment with Docker Compose

# Define Docker Compose file path
COMPOSE_FILE="docker-compose.yml"

# Create Docker Compose file
echo "Creating Docker Compose file..."
cat <<EOL > $COMPOSE_FILE
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  db:
    image: postgres:latest
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app_db
  monitoring:
    image: prom/prometheus
    ports:
      - "9090:9090"
EOL

# Start Docker Compose environment
echo "Starting Docker Compose environment..."
docker-compose up -d

echo "Local development environment setup complete."