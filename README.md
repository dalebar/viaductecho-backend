# Viaduct Echo

**Stockport's local community hub** - News aggregation platform with Python backend, REST API, and native mobile apps. Features AI-powered summaries, multi-platform content delivery, and modern Android/iOS applications.

*Python 3.13 • FastAPI • SQLAlchemy • PostgreSQL • Kotlin • SwiftUI • Material Design 3*

## 🎯 Overview

Viaduct Echo transforms local news consumption with intelligent content aggregation and modern mobile experiences:

- **Smart Aggregation**: Fetches articles from BBC Manchester, Manchester Evening News (RSS), and Stockport Nub News (web scraping)
- **AI Enhancement**: Generates intelligent summaries using OpenAI for faster content consumption
- **Multi-Platform**: REST API backend with native Android and iOS applications
- **Local Focus**: Curated content for Stockport and Greater Manchester communities
- **Modern Architecture**: Clean separation between backend services and mobile frontends

## 📱 Applications

### Android App (Kotlin, Material Design 3)
- **Landing Hub**: 5-section community hub (Local News, Events, Attractions, Offers, Directory)
- **Adaptive Theming**: Automatic light/dark mode with Viaduct Echo brand colors
- **Memory Optimized**: Comprehensive leak auditing and performance improvements
- **Modern UI**: Material Design 3 with custom splash screen and navigation

### iOS App (SwiftUI)
- Native iOS experience with SwiftUI
- Consistent branding across platforms

## 🚀 Recent Achievements (Phase 1-2.2)

### Phase 1: Android App Stabilization ✅
- Comprehensive memory leak audit and fixes
- Null safety improvements and type safety enhancements
- Custom app icon with adaptive theming
- Performance optimizations and resource cleanup

### Phase 2.2: Landing Page Architecture ✅
- Transformed single-purpose news app into 5-section community hub
- Implemented splash screen with Viaduct Echo branding
- Added theme-aware backgrounds and logos
- Stockport-focused messaging and local community sections

## 📁 Project Structure
```
viaductecho-backend/
├── src/                 # Python backend
│   ├── api/            # FastAPI REST API
│   ├── database/       # SQLAlchemy models & operations
│   ├── processors/     # AI summarizer, content extraction
│   ├── sources/        # News source fetchers (BBC, MEN, Nub)
│   └── publishers/     # GitHub Pages publishing
├── android-app/        # Native Android app (Kotlin, Material Design 3)
├── ios-app/           # Native iOS app (SwiftUI)
└── tests/             # Comprehensive test suite
```

## 🛠️ Development Setup

### Prerequisites
- Python 3.13+
- PostgreSQL 15+
- uv package manager
- Android Studio (for Android development)
- Xcode (for iOS development)

### Quick Start
```bash
# Backend setup
cp .env.example .env        # Configure environment variables
make dev-setup             # Install dependencies + pre-commit hooks
make run-api              # Start API server → http://localhost:8000

# Android development
cd android-app
# Open in Android Studio or use gradle commands

# iOS development
cd ios-app
# Open ViaductEcho.xcodeproj in Xcode
```

### Common Commands
- `make run` – Run news aggregator
- `make test` – Execute test suite
- `make lint` – Code quality checks (Ruff + Bandit)
- `make format` – Code formatting (Black + Ruff imports)

## ⚙️ Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

**Required:**
- `DATABASE_URL` - PostgreSQL connection string

**Optional:**
- `OPENAI_API_KEY` - Enable AI-powered article summaries
- `GITHUB_TOKEN`, `GITHUB_REPO`, `GITHUB_BRANCH` - GitHub Pages publishing
- `API_TITLE`, `API_VERSION`, `CORS_ORIGINS` - API customization
- `HTTP_TIMEOUT` - Request timeout for external sources

## 🏗️ Architecture & Quality

### Code Quality
- **Linting**: Ruff (replaces Flake8 + isort)
- **Formatting**: Black with consistent imports
- **Security**: Bandit security analysis
- **Testing**: pytest with coverage reporting
- **Pre-commit**: Automated quality checks

### CI/CD Pipeline
- Automated testing on all platforms
- Code quality enforcement
- Security vulnerability scanning
- Multi-platform compatibility validation

## 🚀 Deployment

### Docker Support
```bash
make docker-build
docker run -p 8000:8000 --env-file .env viaductecho-backend
```

### API Documentation
- Interactive docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

## 🎨 Brand Guidelines

**Viaduct Echo Brand Colors:**
- Dark: `#1b2021`
- Light: `#f7f7ff`
- Brown: `#964436`
- Lime: `#BECC00`

## 📄 License

MIT License - see `LICENSE` file for details.
