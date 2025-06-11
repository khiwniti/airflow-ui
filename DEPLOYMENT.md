# Deployment Guide

This guide explains how to deploy your Airflow project using GitHub instead of Astronomer Cloud.

## 🎯 Deployment Options

### 1. GitHub Codespaces (Recommended for Development)

**Pros:**
- Zero local setup required
- Automatic environment configuration
- Integrated VS Code
- Free for public repositories

**Steps:**
1. Go to your GitHub repository
2. Click "Code" → "Codespaces" → "Create codespace on main"
3. Wait for the environment to initialize
4. Airflow will be available at the forwarded port (8080)

### 2. Local Docker Development

**Pros:**
- Full control over environment
- Works offline
- Good for development and testing

**Steps:**
```bash
# Clone and setup
git clone https://github.com/khiwniti/airflow-ui.git
cd airflow-ui

# Windows
.\scripts\deploy.ps1

# Linux/Mac
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 3. Cloud Deployment Options

#### A. GitHub Container Registry + Cloud Run (Google Cloud)
```bash
# Build and push image
docker build -t gcr.io/your-project/airflow-ui .
docker push gcr.io/your-project/airflow-ui

# Deploy to Cloud Run
gcloud run deploy airflow-ui \
  --image gcr.io/your-project/airflow-ui \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### B. AWS ECS with GitHub Actions
```yaml
# Add to .github/workflows/deploy-aws.yml
- name: Deploy to ECS
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: task-definition.json
    service: airflow-service
    cluster: airflow-cluster
```

#### C. Azure Container Instances
```bash
# Deploy using Azure CLI
az container create \
  --resource-group myResourceGroup \
  --name airflow-ui \
  --image ghcr.io/khiwniti/airflow-ui:latest \
  --ports 8080
```

#### D. DigitalOcean App Platform
```yaml
# app.yaml
name: airflow-ui
services:
- name: web
  source_dir: /
  github:
    repo: khiwniti/airflow-ui
    branch: main
  run_command: docker-compose up
  http_port: 8080
```

## 🔧 Configuration for Production

### Environment Variables
Create production `.env` file:
```bash
# Production settings
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://user:pass@host:5432/airflow
AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
AIRFLOW__CORE__FERNET_KEY=your-fernet-key
AIRFLOW__WEBSERVER__SECRET_KEY=your-secret-key
```

### Security Considerations
1. **Change default passwords**
2. **Use environment variables for secrets**
3. **Enable HTTPS**
4. **Configure authentication (LDAP/OAuth)**
5. **Set up proper firewall rules**

### Scaling Configuration
```yaml
# docker-compose.prod.yml
services:
  airflow-worker:
    <<: *airflow-common
    command: celery worker
    deploy:
      replicas: 3
  
  redis:
    image: redis:7-alpine
    
  flower:
    <<: *airflow-common
    command: celery flower
    ports:
      - "5555:5555"
```

## 🚀 CI/CD Pipeline

The included GitHub Actions workflow automatically:

1. **Tests** DAGs on every push/PR
2. **Builds** Docker images
3. **Pushes** to GitHub Container Registry
4. **Notifies** about deployment status

### Customizing the Pipeline

Edit `.github/workflows/deploy.yml` to add:
- Deployment to your cloud provider
- Integration tests
- Security scanning
- Performance tests

## 📊 Monitoring and Logging

### Built-in Monitoring
- Airflow Web UI: DAG status, task logs
- Flower (if using Celery): Worker monitoring
- PostgreSQL: Database metrics

### External Monitoring
```yaml
# Add to docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

## 🔄 Backup and Recovery

### Database Backup
```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U airflow airflow > backup.sql

# Restore
docker-compose exec -T postgres psql -U airflow airflow < backup.sql
```

### DAG Backup
DAGs are version-controlled in Git, so they're automatically backed up.

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Memory issues**: Increase Docker memory allocation
3. **Permission errors**: Check file permissions and user IDs
4. **Database connection**: Verify PostgreSQL is running

### Logs
```bash
# View all logs
docker-compose logs

# Specific service
docker-compose logs airflow-webserver

# Follow logs
docker-compose logs -f airflow-scheduler
```

## 📈 Performance Optimization

### For Production
1. **Use external database** (RDS, Cloud SQL)
2. **Use external message broker** (Redis, RabbitMQ)
3. **Enable connection pooling**
4. **Configure proper resource limits**
5. **Use SSD storage**

### Resource Requirements
- **Minimum**: 2 CPU, 4GB RAM
- **Recommended**: 4 CPU, 8GB RAM
- **Production**: 8+ CPU, 16+ GB RAM

## 🔐 Security Best Practices

1. **Use secrets management** (AWS Secrets Manager, Azure Key Vault)
2. **Enable audit logging**
3. **Regular security updates**
4. **Network segmentation**
5. **Access control and RBAC**

## 📞 Support

For deployment issues:
1. Check this guide first
2. Review GitHub Issues
3. Check Airflow documentation
4. Create a new issue with deployment details
