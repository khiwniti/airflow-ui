# Airflow Analytics Project

A modern Apache Airflow deployment using GitHub for CI/CD and containerized deployment.

## 🚀 Quick Start

### Option 1: GitHub Codespaces (Recommended)
1. Click the "Code" button on GitHub
2. Select "Create codespace on main"
3. Wait for the environment to load
4. Airflow will be automatically available at the forwarded port

### Option 2: Local Development

#### Prerequisites
- Docker Desktop
- Git

#### Windows (PowerShell)
```powershell
# Clone the repository
git clone https://github.com/khiwniti/airflow-ui.git
cd airflow-ui

# Run deployment script
.\scripts\deploy.ps1
```

#### Linux/Mac (Bash)
```bash
# Clone the repository
git clone https://github.com/khiwniti/airflow-ui.git
cd airflow-ui

# Make script executable and run
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

#### Manual Docker Compose
```bash
# Create directories
mkdir -p logs plugins config

# Start services
docker-compose up -d

# Initialize database (first time only)
docker-compose up airflow-init
```

## 📊 Access Airflow

- **Web UI**: http://localhost:8080
- **Username**: admin
- **Password**: admin123
- **Database**: localhost:5433 (PostgreSQL)

## 🛠️ Management Commands

### Windows PowerShell
```powershell
# View logs
.\scripts\deploy.ps1 -Logs

# Stop services
.\scripts\deploy.ps1 -Stop

# Restart services
.\scripts\deploy.ps1 -Restart
```

### Linux/Mac
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

## 📁 Project Structure

```
├── dags/                   # Airflow DAGs
├── plugins/               # Custom plugins
├── include/               # Additional files
├── tests/                 # DAG tests
├── scripts/               # Deployment scripts
├── .github/workflows/     # CI/CD pipelines
├── .devcontainer/         # Codespaces config
├── docker-compose.yml     # Local deployment
├── Dockerfile            # Custom Airflow image
└── requirements.txt      # Python dependencies
```

## 🔄 CI/CD Pipeline

The project includes automated GitHub Actions workflows:

- **Testing**: Runs DAG validation and tests on every PR
- **Building**: Creates Docker images and pushes to GitHub Container Registry
- **Deployment**: Automated deployment notifications

## 🌐 Deployment Options

### 1. GitHub Codespaces
- Zero setup required
- Automatic port forwarding
- Integrated VS Code environment

### 2. Local Docker
- Full control over environment
- Suitable for development
- Uses docker-compose for orchestration

### 3. Cloud Deployment
- GitHub Container Registry images
- Ready for Kubernetes deployment
- Scalable production setup

## 🧪 Testing

```bash
# Run DAG tests
python -m pytest tests/ -v

# Validate DAGs
python -c "from airflow.models import DagBag; db = DagBag(); print('DAGs loaded successfully' if not db.import_errors else db.import_errors)"
```

## 📝 Adding New DAGs

1. Create Python files in the `dags/` directory
2. Follow Airflow DAG conventions
3. Test locally before committing
4. Push to GitHub for automatic deployment

## 🔧 Configuration

- **Environment variables**: `.env` file
- **Airflow settings**: `airflow_settings.yaml`
- **Python packages**: `requirements.txt`
- **System packages**: `packages.txt`

## 🆘 Troubleshooting

### Port Conflicts
If port 5432 is in use:
```bash
# Check what's using the port
netstat -ano | findstr :5432

# Stop PostgreSQL service (Windows)
Stop-Service postgresql*
```

### Container Issues
```bash
# Check container status
docker-compose ps

# View specific service logs
docker-compose logs airflow-webserver

# Restart specific service
docker-compose restart airflow-scheduler
```

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review Airflow documentation
