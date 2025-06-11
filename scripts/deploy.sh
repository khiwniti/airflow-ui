#!/bin/bash

# Airflow Deployment Script for GitHub
set -e

echo "🚀 Starting Airflow deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ./logs ./plugins ./config

# Set proper permissions (Linux/Mac only)
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🔐 Setting permissions..."
    echo -e "AIRFLOW_UID=$(id -u)" > .env.local
    source .env.local
fi

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker-compose pull

# Initialize Airflow database
echo "🗄️ Initializing Airflow database..."
docker-compose up airflow-init

# Start all services
echo "🎯 Starting Airflow services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if webserver is running
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Airflow is running successfully!"
    echo "🌐 Web UI: http://localhost:8080"
    echo "👤 Username: admin"
    echo "🔑 Password: admin123"
    echo ""
    echo "📊 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
else
    echo "❌ Airflow webserver is not responding. Check logs with: docker-compose logs"
    exit 1
fi
