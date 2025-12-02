# Viaduct Echo

**Stockport's local community hub** - News aggregation platform with Python backend, REST API, and native mobile apps. Features AI-powered summaries, multi-platform content delivery, local events integration, and modern Android/iOS applications.

*Python 3.13 • FastAPI • SQLAlchemy • PostgreSQL • Skiddle API • Kotlin • SwiftUI • Material Design 3*

## 🎯 Overview

Viaduct Echo transforms local news and events consumption with intelligent content aggregation and modern mobile experiences:

- **Smart Aggregation**: Fetches articles from BBC Manchester, Manchester Evening News (RSS), and Stockport Nub News (web scraping)
- **Local Events**: Integration with Skiddle API for Greater Manchester events (3-mile radius from Stockport)
- **AI Enhancement**: Generates intelligent summaries using OpenAI for faster content consumption
- **Admin Dashboard**: Web-based management interface for events, venues, and content publishing
- **Auto-Publishing**: Automated deployment to GitHub Pages via REST API
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

### Jekyll Website
- Static site hosted on GitHub Pages
- Events listing with filtering and calendar view
- Automated deployment via admin dashboard

## 🚀 Recent Achievements

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

### Phase 3: Events System ✅
- **Database & Models**: Events and venues tables with SQLAlchemy models
- **Skiddle API Integration**: Automated event fetching (3-mile radius from Stockport center)
- **REST API Endpoints**: Full CRUD operations for events and venues
- **Admin Dashboard**: Web-based management interface at `/admin`
  - Events and venues management
  - Image upload for event photos
  - One-click publish to Jekyll site
- **Jekyll Frontend**: Events listing and calendar view pages
- **Auto-Publishing**: GitHub API integration for automated deployment

## 📁 Project Structure
```
viaductecho-backend/
├── src/                      # Python backend
│   ├── api/                 # FastAPI REST API
│   │   ├── routes/         # API endpoints (articles, events, venues, admin)
│   │   ├── schemas/        # Pydantic validation schemas
│   │   └── static/         # Admin dashboard HTML
│   ├── database/           # SQLAlchemy models & operations
│   │   ├── models.py      # RSSArticle, Event, Venue models
│   │   ├── operations.py  # Article database operations
│   │   └── event_operations.py  # Event/venue operations
│   ├── processors/         # AI summarizer, content extraction
│   ├── sources/           # News source fetchers (BBC, MEN, Nub)
│   ├── publishers/        # GitHub Pages publishing
│   ├── events_aggregator.py  # Skiddle API integration
│   └── config.py          # Configuration and environment variables
├── android-app/           # Native Android app (Kotlin, Material Design 3)
├── ios-app/              # Native iOS app (SwiftUI)
├── static/event_images/  # Uploaded event images (not in git)
├── static_data/          # Generated JSON files for Jekyll (not in git)
└── tests/                # Comprehensive test suite
```

## 🛠️ Development Setup

### Prerequisites
- Python 3.13+
- PostgreSQL 15+ (or Neon hosted database)
- uv package manager
- Android Studio (for Android development)
- Xcode (for iOS development)

### Quick Start
```bash
# Backend setup
cp .env.example .env        # Configure environment variables
make dev-setup             # Install dependencies + pre-commit hooks
make run-api              # Start API server → http://localhost:8000

# Access admin dashboard
open http://localhost:8000/admin

# Android development
cd android-app
# Open in Android Studio or use gradle commands

# iOS development
cd ios-app
# Open ViaductEcho.xcodeproj in Xcode
```

### Common Commands
- `make run` – Run news aggregator
- `make run-api` – Start FastAPI server
- `make test` – Execute test suite
- `make lint` – Code quality checks (Ruff + Bandit)
- `make format` – Code formatting (Black + Ruff imports)

## ⚙️ Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

**Required:**
- `DATABASE_URL` - PostgreSQL connection string (Neon hosted)
- `ADMIN_API_KEY` - API key for admin dashboard authentication

**Events Integration:**
- `SKIDDLE_API_KEY` - API key for Skiddle events service
- `STOCKPORT_LAT` - Latitude for event search center (default: 53.4106)
- `STOCKPORT_LON` - Longitude for event search center (default: -2.1575)
- `EVENT_SEARCH_RADIUS` - Search radius in miles (default: 3)

**GitHub Pages Publishing:**
- `GITHUB_TOKEN` - Personal access token with repo permissions
- `GITHUB_REPO` - Repository in format `username/repo`
- `GITHUB_BRANCH` - Target branch (default: main)

**Optional:**
- `OPENAI_API_KEY` - Enable AI-powered article summaries
- `API_TITLE`, `API_VERSION`, `CORS_ORIGINS` - API customization
- `HTTP_TIMEOUT` - Request timeout for external sources

## 🎛️ Admin Dashboard

Access the admin dashboard at `http://localhost:8000/admin` (or `https://api.viaductecho.info/admin` in production).

**Features:**
- **Events Management**: Create, edit, delete, and feature events
- **Venues Management**: Manage event venues with full details
- **Image Upload**: Upload event photos (max 5MB, JPG/PNG/GIF/WEBP)
- **Publish to Jekyll**: One-click aggregation and deployment to GitHub Pages
- **Dashboard Stats**: Real-time overview of events, venues, and featured content

**Authentication:**
Use the `ADMIN_API_KEY` from your `.env` file to log in.

## 🌐 API Endpoints

### Public Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - Health check with database status
- `GET /api/v1/articles` - List articles with pagination and filtering
- `GET /api/v1/articles/{id}` - Get article details
- `GET /api/v1/sources` - List news sources
- `GET /api/v1/events` - List upcoming events with filtering
- `GET /api/v1/events/{id}` - Get event details
- `GET /api/v1/venues` - List venues
- `GET /api/v1/venues/{id}` - Get venue details

### Admin Endpoints (API Key Required)
- `POST /api/v1/admin/events` - Create event
- `PATCH /api/v1/admin/events/{id}` - Update event
- `DELETE /api/v1/admin/events/{id}` - Delete event
- `POST /api/v1/admin/venues` - Create venue
- `PATCH /api/v1/admin/venues/{id}` - Update venue
- `DELETE /api/v1/admin/venues/{id}` - Delete venue
- `POST /api/v1/admin/upload-image` - Upload event image
- `POST /api/v1/admin/aggregate` - Run aggregation and publish to GitHub Pages

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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

### Events System Architecture
1. **Skiddle API** → Fetches events within 3-mile radius
2. **Database** → PostgreSQL with events/venues tables
3. **FastAPI** → REST endpoints for CRUD operations
4. **Admin Dashboard** → Web UI for content management
5. **Static JSON** → Generated files for Jekyll site
6. **GitHub API** → Automated push to GitHub Pages
7. **Jekyll Site** → Auto-deploys with updated events

## 🚀 Deployment

### EC2 Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Run with uvicorn
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4

# Or use systemd service for production
```

### API Documentation
- Interactive docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`
- Admin dashboard: `http://localhost:8000/admin`

## 🎨 Brand Guidelines

**Viaduct Echo Brand Colors:**
- Dark: `#1b2021`
- Light: `#f7f7ff`
- Brown: `#964436`
- Lime: `#BECC00`

## 📄 License

MIT License - see `LICENSE` file for details.
