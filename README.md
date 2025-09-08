# Viaduct Echo Backend

A comprehensive news aggregation platform for Greater Manchester, featuring Python backend services, REST API, native mobile applications, and enterprise-grade development tooling.

[![CI Pipeline](https://github.com/your-username/viaductecho-backend/workflows/CI%20Pipeline/badge.svg)](https://github.com/your-username/viaductecho-backend/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Flake8](https://img.shields.io/badge/linting-flake8-blue)](https://flake8.pycqa.org/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## 🏗️ Architecture Overview

Viaduct Echo is a production-ready news aggregation platform with enterprise-grade tooling:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   News Sources  │───▶│   Aggregation    │───▶│    Database     │
│  • BBC RSS      │    │   & Processing   │    │   PostgreSQL    │
│  • MEN RSS      │    │  • Filtering     │    │                 │
│  • Nub Scraping │    │  • Extraction    │    │                 │
└─────────────────┘    │  • AI Summary    │    └─────────────────┘
                       └──────────────────┘             │
                                                        │
┌─────────────────┐    ┌──────────────────┐            │
│  GitHub Pages   │◀───│    Publishers    │◀───────────┘
│   Jekyll Site   │    │  • GitHub Pages  │
│                 │    │  • REST API      │
│                 │    │  • Mobile Apps   │
└─────────────────┘    └──────────────────┘
```

**Project Structure**:
```
viaductecho-backend/
├── src/                    # Python backend services
│   ├── api/               # FastAPI REST server  
│   ├── database/          # PostgreSQL operations + utilities
│   ├── processors/        # AI summarization & content extraction
│   ├── sources/           # Multi-source news aggregation  
│   └── publishers/        # GitHub Pages publishing
├── android-app/           # Kotlin Android application
├── ios-app/               # SwiftUI iOS application  
├── tests/                 # Comprehensive test suite (225+ tests)
├── .github/workflows/     # CI/CD automation
├── logs/                  # Organized logging system
└── Makefile              # Development automation
```

## 🚀 Features

### Backend Services
- **Multi-source aggregation**: RSS feeds (BBC, MEN) and web scraping (Nub News)
- **AI-powered processing**: OpenAI article summarization with GPT-4
- **REST API**: FastAPI server with comprehensive endpoints and OpenAPI docs
- **Intelligent filtering**: Keyword-based local relevance detection
- **Robust database**: PostgreSQL with automatic reconnection and optimized indexing
- **Automated publishing**: GitHub Pages Jekyll integration
- **Enterprise logging**: Structured logging with session and API tracking

### Mobile Applications
- **Android App (Kotlin)**: Native Material Design 3 interface with MVVM architecture
- **iOS App (SwiftUI)**: Clean, modern design with real-time data synchronization
- **Shared Features**: Article browsing, AI summary display, image loading, offline support

### Development & Quality Assurance
- **Automated code quality**: Black formatting, Flake8 linting, pre-commit hooks
- **Comprehensive testing**: 225+ automated tests with >90% coverage
- **CI/CD pipeline**: GitHub Actions with multi-stage deployment
- **Development automation**: Makefile with 25+ commands for common tasks
- **Security scanning**: Bandit integration for vulnerability detection
- **Type safety**: MyPy static analysis for enhanced code reliability

## 🛠️ Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL 15+ (or cloud database like Neon)
- OpenAI API key
- GitHub personal access token
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### One-Command Setup

```bash
# Complete development environment setup
make dev-setup
```

This single command:
- ✅ Installs all dependencies with uv
- ✅ Sets up pre-commit hooks
- ✅ Configures development tools
- ✅ Validates environment setup

### Manual Setup (Alternative)

1. **Environment setup**:
   ```bash
   # Using uv (recommended)
   uv sync --dev
   
   # Using pip
   pip install -r requirements.txt
   
   # Install pre-commit hooks
   uv run pre-commit install
   ```

2. **Environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Database verification**:
   ```bash
   # Check database and AI summary status
   make db-status
   ```

4. **Run services**:
   ```bash
   # News aggregation service
   make run
   
   # API development server
   make run-api
   ```

## 📱 Mobile Applications

### Android App (Kotlin + Jetpack Compose)
**Status**: ✅ Production Ready

**Features**:
- Material Design 3 theming with NoActionBar configuration
- MVVM architecture with Hilt dependency injection  
- Retrofit API integration with proper error handling
- Article list with AI summaries and image loading
- KSP-based annotation processing (Kotlin 2.0+ compatible)
- Comprehensive cleanup and optimization completed

**Development**:
```bash
# Open in Android Studio
open android-app/
```

### iOS App (SwiftUI)
**Status**: ✅ Complete and tested

**Features**:
- Native SwiftUI interface with clean design
- Real-time article updates via REST API
- AsyncImage loading with proper placeholders
- Article detail views with AI summaries
- Graceful error handling and retry mechanisms

**Development**:
```bash
# Open in Xcode  
open ios-app/ViaductEcho.xcodeproj
```

## ⚡ Development Workflow

### Available Commands

Our comprehensive Makefile provides 25+ development commands:

```bash
make help                 # Show all available commands

# Development Setup
make dev-setup           # Complete development environment setup
make install-dev         # Install development dependencies with pre-commit

# Code Quality
make format              # Auto-format with black and isort
make lint                # Run flake8 linting and security checks
make dev-check           # Run all quality checks (format + lint + tests)
make pre-commit          # Run all pre-commit hooks

# Testing
make test                # Run full test suite with pytest
make test-coverage       # Generate HTML coverage reports
make ci                  # Run complete CI pipeline locally

# Application
make run                 # Start news aggregation service
make run-api             # Start FastAPI development server
make db-status           # Check AI summary database status
make db-backfill         # Backfill AI summaries for existing articles

# Docker & Deployment
make docker-build        # Build production Docker image
make docker-up           # Start production services
make docker-dev          # Start development environment
make docker-logs         # View container logs

# Maintenance
make clean               # Clean caches and temporary files
make info                # Show project and environment information
```

### Code Quality Standards

Our automated quality assurance includes:

**Formatting & Style**:
- **Black**: Code formatting with 88-character line length
- **isort**: Import sorting with black-compatible profile
- **Flake8**: Comprehensive linting with custom rules

**Analysis & Security**:
- **MyPy**: Static type checking for enhanced reliability
- **Bandit**: Security vulnerability scanning
- **Pre-commit hooks**: Automated quality checks on every commit

**Testing & Coverage**:
- **pytest**: 225+ comprehensive tests
- **Coverage**: >90% code coverage with HTML reports
- **Integration tests**: End-to-end workflow validation

### CI/CD Pipeline

**Continuous Integration** (runs on every push/PR):
- ✅ Code formatting validation (Black, isort)
- ✅ Linting and security checks (Flake8, Bandit)  
- ✅ Full test suite with coverage reporting
- ✅ Type checking with MyPy
- ✅ Multi-platform Docker builds
- ✅ Integration with PostgreSQL services

**Release Pipeline** (automated deployments):
- 🚀 Multi-architecture Docker image builds  
- 🚀 Staging environment deployment
- 🚀 Production deployment with approval gates
- 🚀 Semantic versioning and changelog generation

## 🔧 API Documentation

**Base URL**: `http://localhost:8000`
**Interactive Docs**: `/docs` (Swagger UI) and `/redoc` (ReDoc)

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health and database status |
| `GET` | `/api/articles` | Paginated articles with filtering |
| `GET` | `/api/articles/{id}` | Individual article with AI summary |
| `GET` | `/api/articles/recent` | Recent articles (default: 50) |
| `GET` | `/api/sources` | News source statistics |
| `GET` | `/api/sources/{source}/articles` | Source-specific articles |

### Example API Response

```json
{
  "articles": [
    {
      "id": 1,
      "title": "Local Development News",
      "source": "BBC Manchester",
      "published_date": "2025-09-08T12:00:00Z",
      "image_url": "https://example.com/image.jpg",
      "ai_summary": "AI-generated concise summary...",
      "extracted_content": "Full article content...",
      "url": "https://bbc.co.uk/news/article"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 12,
    "total_articles": 235,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🗄️ Database Schema

**Primary Table**: `rss_articles`

```sql
CREATE TABLE rss_articles (
    id SERIAL PRIMARY KEY,
    original_title VARCHAR(500) NOT NULL,
    original_link TEXT UNIQUE NOT NULL,
    original_summary TEXT,
    original_source VARCHAR(100) NOT NULL,
    source_type VARCHAR(50),
    original_pubdate TIMESTAMP WITH TIME ZONE,
    url_hash VARCHAR(64) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    extracted_content TEXT,
    ai_summary TEXT,
    image_url TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_articles_source ON rss_articles(original_source);
CREATE INDEX idx_articles_pubdate ON rss_articles(original_pubdate DESC);
CREATE INDEX idx_articles_processed ON rss_articles(processed);
```

**Database Utilities**:
```bash
make db-status    # Check database health and AI summary completion
make db-backfill  # Generate AI summaries for articles missing them
```

## 🧪 Testing Framework

Our comprehensive test suite ensures reliability:

**Test Coverage** (225+ automated tests):
- **API Operations**: 19 tests - Endpoint validation, pagination, error handling
- **Database Operations**: 12 tests - CRUD operations, connection management
- **Content Processing**: 34 tests - AI summarization, content extraction
- **News Sources**: 53 tests - RSS parsing, web scraping, keyword filtering  
- **GitHub Publishing**: 14 tests - Jekyll formatting, API integration
- **Error Handling**: 45 tests - Edge cases, validation, recovery mechanisms
- **Integration Tests**: 48+ tests - End-to-end workflow validation

**Run Tests**:
```bash
# Full test suite
make test

# With coverage report  
make test-coverage

# Specific test categories
pytest tests/api/ -v           # API endpoint tests
pytest tests/test_*.py -v      # Component tests
```

## 🐳 Docker & Deployment

### Development Environment

```bash
# Start full development stack
make docker-dev

# Individual services
make docker-up      # Production containers
make docker-logs    # View container logs  
make docker-down    # Stop all services
```

**Docker Compose Services**:
- **PostgreSQL 15**: Database with health checks and data persistence
- **API Server**: FastAPI with hot reloading in development mode  
- **News Aggregator**: Background service for article fetching
- **Redis**: Caching layer for enhanced performance

### Production Deployment

**Container Deployment**:
```bash
# Build optimized production image
make docker-build

# Deploy with environment variables
docker run -d -p 8000:8000 --env-file .env viaductecho-backend
```

**Traditional Deployment**:
```bash
# Production API server
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4

# Scheduled aggregation (systemd/cron)
0 */2 8-22 * * * /path/to/python -m src.main
```

## 📊 News Sources & Geographic Coverage

### Configured Sources
- **BBC Manchester**: RSS feed with intelligent local filtering
- **Manchester Evening News**: Greater Manchester regional coverage
- **Stockport Nub News**: Web scraping with JSON-LD structured data extraction

### Coverage Areas
**Primary Locations**: Stockport, Manchester, Macclesfield, Wilmslow, Altrincham

**Extended Coverage**:
- **Manchester Districts**: Chorlton, Didsbury, Fallowfield, Withington, Wythenshawe
- **Greater Manchester**: Oldham, Rochdale, Bury, Bolton, Salford, Tameside
- **High Peak**: Buxton, Glossop, New Mills, Chapel-en-le-Frith, Whaley Bridge

*Complete keyword configuration in `src/config.py`*

## 🤝 Contributing

We welcome contributions! Our development process ensures code quality:

### Development Process

1. **Setup development environment**:
   ```bash
   make dev-setup
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Development with quality checks**:
   ```bash
   # Automatic formatting and linting
   make dev-check
   
   # Run tests during development
   make test
   ```

4. **Pre-commit validation**:
   ```bash
   # Runs automatically on git commit
   # Or manually: make pre-commit
   ```

5. **Submit pull request** - CI pipeline validates all changes

### Quality Gates

All contributions must pass:
- ✅ **Code Formatting**: Black and isort validation
- ✅ **Linting**: Flake8 compliance with zero violations  
- ✅ **Security**: Bandit vulnerability scanning
- ✅ **Testing**: Full test suite with maintained coverage
- ✅ **Type Safety**: MyPy static analysis
- ✅ **Integration**: Docker build verification

### Development Guidelines
- **Commits**: Use conventional commit messages (`feat:`, `fix:`, `docs:`)
- **Testing**: Add comprehensive tests for new functionality
- **Documentation**: Update README and docstrings
- **Code Style**: Follow established patterns and formatting

## 📈 System Status

### ✅ Production Ready Components
- **Backend Services**: News aggregation, API server, database operations
- **Mobile Applications**: Android (Kotlin) and iOS (SwiftUI) apps
- **Development Tooling**: Complete automation and quality assurance
- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Database Management**: Utilities for AI summary management and health monitoring
- **Code Quality**: Zero linting violations, comprehensive test coverage

### 🚧 Future Enhancements
- **Analytics Dashboard**: Web interface for content management and metrics
- **Push Notifications**: Real-time article alerts for mobile apps
- **Offline Synchronization**: Enhanced offline support with conflict resolution
- **Performance Optimization**: Caching strategies and database query optimization
- **Multi-language Support**: Internationalization framework

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-username/viaductecho-backend/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/viaductecho-backend/discussions)  
- 📖 **Documentation**: Available at `/docs` endpoint and in repository `/docs` directory
- 🔧 **Development Help**: Run `make help` for available commands
- 🌐 **API Documentation**: Interactive docs at `http://localhost:8000/docs`

---

**Latest Update**: v2.0.0 - Complete platform with enterprise-grade development tooling, automated quality assurance, comprehensive CI/CD, and production-ready mobile applications.