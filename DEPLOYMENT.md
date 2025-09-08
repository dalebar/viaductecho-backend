# Viaduct Echo API Deployment Guide

This guide covers deploying the Viaduct Echo API using Docker and Docker Compose.

## Quick Start

### Development Environment

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd viaductecho-backend
   cp .env.example .env.dev
   ```

2. **Configure environment variables** in `.env.dev`:
   ```env
   DATABASE_URL=postgresql://dev_user:dev_password@postgres:5432/viaduct_echo_dev
   OPENAI_API_KEY=your_openai_api_key
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO=your_username/your_repo
   GITHUB_BRANCH=main
   ```

3. **Start development environment**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

4. **Access the API**:
   - API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs
   - Database: localhost:5433

### Production Environment

1. **Configure production environment** in `.env`:
   ```env
   DATABASE_URL=postgresql://viaduct:secure_password@postgres:5432/viaduct_echo
   OPENAI_API_KEY=your_openai_api_key
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO=your_username/your_repo
   GITHUB_BRANCH=main
   
   # Optional API configuration
   API_TITLE="Viaduct Echo API"
   API_VERSION="1.0.0"
   CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
   DEFAULT_PAGE_SIZE=20
   MAX_PAGE_SIZE=100
   ```

2. **Start production environment**:
   ```bash
   docker-compose up -d
   ```

3. **Access the API**:
   - API: http://localhost:8000
   - Health check: http://localhost:8000/health

## Services

### API Service
- **Port**: 8000 (production), 8001 (development)
- **Health check**: `/health` endpoint
- **Documentation**: `/docs` (Swagger) and `/redoc`
- **Workers**: 4 (production), 1 with reload (development)

### Database Service
- **Type**: PostgreSQL 15
- **Port**: 5432 (production), 5433 (development)
- **Initialization**: Automatic table creation with sample data
- **Persistence**: Docker volume `postgres_data`

### Aggregator Service
- **Function**: Runs the news aggregation scheduler
- **Schedule**: Every 2 hours between 8 AM - 10 PM
- **Sources**: BBC, Manchester Evening News, Stockport Nub News

### Redis Service (Optional)
- **Function**: Caching for future enhancements
- **Port**: 6379
- **Persistence**: Docker volume `redis_data`

## Database Management

### Initialize Database
The database is automatically initialized with tables and sample data when the PostgreSQL container starts for the first time.

### Manual Database Operations
```bash
# Connect to database
docker-compose exec postgres psql -U viaduct -d viaduct_echo

# Run migrations (if needed)
docker-compose exec api python -c "from src.database.operations import DatabaseOperations; DatabaseOperations().create_tables()"

# View database logs
docker-compose logs postgres
```

### Backup and Restore
```bash
# Backup
docker-compose exec postgres pg_dump -U viaduct viaduct_echo > backup.sql

# Restore
docker-compose exec -T postgres psql -U viaduct -d viaduct_echo < backup.sql
```

## Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f aggregator
docker-compose logs -f postgres
```

### Health Monitoring
- **API Health**: `curl http://localhost:8000/health`
- **Database Health**: Built-in PostgreSQL health checks
- **Service Status**: `docker-compose ps`

### Performance Monitoring
```bash
# Resource usage
docker stats

# Service resource usage
docker-compose top
```

## Development Workflow

### Running Tests
```bash
# In development container
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec api python -m pytest

# Or run tools container
docker-compose --profile tools run dev-tools python -m pytest
```

### Database Development
```bash
# Access development database
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec postgres psql -U dev_user -d viaduct_echo_dev

# Run development tools
docker-compose --profile tools run dev-tools bash
```

### Code Changes
With development setup, code changes are automatically reloaded thanks to volume mounts and uvicorn's reload feature.

## Scaling and Production

### Horizontal Scaling
```bash
# Scale API service
docker-compose up -d --scale api=3

# Use load balancer (nginx example)
# Add nginx service to docker-compose.yml
```

### Production Hardening

1. **Security**:
   - Use strong database passwords
   - Restrict CORS origins
   - Enable rate limiting
   - Use HTTPS in production
   - Keep API keys secure

2. **Performance**:
   - Increase worker count based on CPU cores
   - Add Redis caching
   - Configure PostgreSQL for production
   - Monitor resource usage

3. **Reliability**:
   - Set up proper logging aggregation
   - Configure alerts for health check failures
   - Implement backup strategy
   - Use container orchestration (Docker Swarm/Kubernetes)

## Environment Variables Reference

### Database
- `DATABASE_URL`: PostgreSQL connection string

### API Configuration
- `API_TITLE`: API title for documentation
- `API_VERSION`: API version
- `API_DESCRIPTION`: API description
- `CORS_ORIGINS`: Comma-separated allowed origins
- `DEFAULT_PAGE_SIZE`: Default pagination size (20)
- `MAX_PAGE_SIZE`: Maximum pagination size (100)

### Rate Limiting
- `RATE_LIMIT_ENABLED`: Enable rate limiting (false)
- `RATE_LIMIT_REQUESTS`: Requests per window (100)
- `RATE_LIMIT_WINDOW`: Window in seconds (60)

### External Services
- `OPENAI_API_KEY`: OpenAI API key for article summarization
- `GITHUB_TOKEN`: GitHub personal access token
- `GITHUB_REPO`: GitHub repository (username/repo)
- `GITHUB_BRANCH`: Target branch (main)

## Troubleshooting

### Common Issues

1. **Database connection failed**:
   - Check database service is running: `docker-compose ps postgres`
   - Verify DATABASE_URL is correct
   - Check database logs: `docker-compose logs postgres`

2. **API not responding**:
   - Check API health: `curl http://localhost:8000/health`
   - View API logs: `docker-compose logs api`
   - Verify environment variables are set

3. **Tests failing**:
   - Ensure development database is running
   - Check test database connection
   - Run tests in isolation: `python -m pytest tests/api/test_health.py -v`

4. **Permission errors**:
   - Check file permissions in container
   - Verify app user ownership: `docker-compose exec api ls -la`

### Getting Help

```bash
# Container information
docker-compose config

# Service health
docker-compose ps

# Resource usage
docker system df
docker system prune  # Clean up unused resources
```