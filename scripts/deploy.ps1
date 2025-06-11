# Airflow Deployment Script for Windows/PowerShell
param(
    [switch]$Stop,
    [switch]$Restart,
    [switch]$Logs
)

Write-Host "🚀 Airflow Deployment Script" -ForegroundColor Green

if ($Stop) {
    Write-Host "🛑 Stopping Airflow services..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✅ Airflow stopped successfully!" -ForegroundColor Green
    exit 0
}

if ($Logs) {
    Write-Host "📊 Showing Airflow logs..." -ForegroundColor Cyan
    docker-compose logs -f
    exit 0
}

if ($Restart) {
    Write-Host "🔄 Restarting Airflow services..." -ForegroundColor Yellow
    docker-compose down
    Start-Sleep -Seconds 5
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "❌ docker-compose is not available. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path ".\logs" | Out-Null
New-Item -ItemType Directory -Force -Path ".\plugins" | Out-Null
New-Item -ItemType Directory -Force -Path ".\config" | Out-Null

# Pull latest images
Write-Host "📦 Pulling latest Docker images..." -ForegroundColor Cyan
docker-compose pull

# Initialize Airflow database
Write-Host "🗄️ Initializing Airflow database..." -ForegroundColor Cyan
docker-compose up airflow-init

# Start all services
Write-Host "🎯 Starting Airflow services..." -ForegroundColor Cyan
docker-compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check if webserver is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Airflow is running successfully!" -ForegroundColor Green
        Write-Host "🌐 Web UI: http://localhost:8080" -ForegroundColor Cyan
        Write-Host "👤 Username: admin" -ForegroundColor Cyan
        Write-Host "🔑 Password: admin123" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📊 To view logs: .\scripts\deploy.ps1 -Logs" -ForegroundColor Yellow
        Write-Host "🛑 To stop: .\scripts\deploy.ps1 -Stop" -ForegroundColor Yellow
        Write-Host "🔄 To restart: .\scripts\deploy.ps1 -Restart" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Airflow webserver is not responding. Check logs with: docker-compose logs" -ForegroundColor Red
    exit 1
}
