# Viaduct Echo

A comprehensive news aggregation platform for Greater Manchester, featuring Python backend services, REST API, and native mobile applications.

## 🏗️ Architecture Overview

Viaduct Echo consists of multiple integrated components:

```
viaductecho-backend/
├── src/                    # Python backend services
│   ├── api/               # FastAPI REST server
│   ├── database/          # PostgreSQL operations
│   ├── processors/        # AI summarization & content extraction
│   ├── sources/           # Multi-source news aggregation
│   └── publishers/        # GitHub Pages publishing
├── ios-app/               # SwiftUI iOS application
├── tests/                 # Comprehensive test suite (225+ tests)
├── logs/                  # Organized logging system
│   ├── sessions/          # Aggregation process logs
│   └── api/              # API server logs
└── docs/                  # Documentation
```

## 🚀 Features

### Backend Services
- **Multi-source aggregation**: RSS feeds (BBC, MEN) and web scraping (Nub News)
- **AI-powered processing**: OpenAI article summarization and image extraction
- **REST API**: FastAPI server with comprehensive endpoints
- **Intelligent filtering**: Keyword-based local relevance detection
- **Robust database**: PostgreSQL with automatic reconnection and indexing
- **Automated publishing**: GitHub Pages Jekyll integration
- **Comprehensive logging**: Session and API logs with timestamps

### iOS Application
- **Native SwiftUI interface**: Clean, modern design
- **Real-time data**: Connects to REST API for live article updates
- **Image loading**: AsyncImage with proper placeholders
- **Article details**: Full content view with AI summaries
- **Error handling**: Graceful failure states and retry mechanisms

### Quality & Testing
- **225+ automated tests**: Full coverage of all components
- **Performance optimized**: Sub-1.2s API response times
- **Code quality**: Flake8 compliance, comprehensive error handling
- **Production ready**: Rigorous testing protocol completed

## 📱 Mobile Applications

### iOS App (SwiftUI)
**Status**: ✅ Complete and tested

**Features**:
- Article list with images and metadata
- Detailed article view with AI summaries
- Clean UI without redundant content
- Proper error handling and loading states
- Integration with REST API backend

### Android App
**Status**: 📋 Planned

**Implementation Options**:
- Native Kotlin (~2-3 weeks)
- Flutter cross-platform (~1-2 weeks)
- React Native (~1-2 weeks)

## 🛠️ Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL database (Neon recommended)
- OpenAI API key
- GitHub personal access token
- Xcode (for iOS development)

### Backend Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # or using uv
   uv sync
   ```

2. **Environment configuration**:
   ```env
   # Database
   DATABASE_URL=postgresql://username:password@host:port/database
   
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   
   # GitHub
   GITHUB_TOKEN=your_github_personal_access_token
   GITHUB_REPO=username/repository-name
   GITHUB_BRANCH=main
   ```

3. **Run news aggregation**:
   ```bash
   python -m src.main
   ```

4. **Start API server**:
   ```bash
   python -m src.api.app
   # Server runs on http://0.0.0.0:8000
   ```

### iOS App Setup

1. **Open in Xcode**:
   ```bash
   open ios-app/ViaductEcho.xcodeproj
   ```

2. **Update API endpoint** in `APIService.swift` if needed

3. **Build and run** in iOS Simulator or device

## 🔧 API Endpoints

**Base URL**: `http://localhost:8000`

### Core Endpoints
- `GET /health` - API and database health check
- `GET /api/v1/articles` - Paginated article list with filters
- `GET /api/v1/articles/{id}` - Individual article details
- `GET /api/v1/sources` - Source statistics
- `GET /api/v1/articles/recent` - Recent articles
- `GET /api/v1/articles/search` - Search functionality

### Example Responses
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Local News Title",
      "source": "BBC News",
      "published_date": "2025-09-02T19:00:00Z",
      "image_url": "https://example.com/image.jpg",
      "ai_summary": "AI-generated summary..."
    }
  ],
  "pagination": {
    "page": 1,
    "total_pages": 5,
    "has_next": true
  }
}
```

## 🗂️ Database Schema

**Table**: `rss_articles`

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
```

**Indexes**: Optimized for API performance on frequently queried columns

## 🧪 Testing

### Run Tests
```bash
# Full test suite (225+ tests)
python -m pytest tests/ -v

# Specific components
python -m pytest tests/api/ -v                    # API tests
python -m pytest tests/test_database_operations.py -v  # Database tests
python -m pytest tests/test_ai_summarizer.py -v        # AI tests

# Coverage report
python -m pytest --cov=src --cov-report=html
```

### Test Coverage
- **API Operations**: 19 tests - Endpoints, pagination, error handling
- **Database Operations**: 12 tests - CRUD, reconnection, transactions
- **Content Processing**: 34 tests - Extraction, AI summarization
- **News Sources**: 53 tests - RSS parsing, web scraping, filtering
- **GitHub Publishing**: 14 tests - Jekyll formatting, API integration
- **Error Handling**: 45 tests - Edge cases, validation, recovery
- **Integration Tests**: 48+ tests - End-to-end workflows

## 🏭 Production Deployment

### Backend Services
```bash
# Production API server
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4

# Scheduled aggregation (cron)
0 */2 8-22 * * * /path/to/python -m src.main
```

### Monitoring
- **Health endpoint**: `/health` for uptime monitoring
- **Structured logging**: Organized in `logs/sessions/` and `logs/api/`
- **Database monitoring**: Connection pooling with automatic recovery
- **Performance metrics**: Response time tracking built-in

## 📊 News Sources & Filtering

### Configured Sources
- **BBC Manchester**: RSS feed with local filtering
- **Manchester Evening News**: Greater Manchester news RSS
- **Stockport Nub News**: Web scraping with JSON-LD extraction

### Geographic Coverage
Keywords target Greater Manchester area including:
- **Primary**: Stockport, Manchester, Macclesfield, Wilmslow, Altrincham
- **Manchester**: Chorlton, Didsbury, Fallowfield, Withington, Wythenshawe
- **Greater Manchester**: Oldham, Rochdale, Bury, Bolton, Salford
- **High Peak**: Buxton, Glossop, New Mills, Chapel-en-le-Frith

*Full keyword list in `src/config.py`*

## 🔄 Development Workflow

### Adding Features
1. **Backend**: Extend API endpoints, add database operations
2. **iOS**: Update SwiftUI views, modify API service calls
3. **Android**: Plan implementation using established patterns
4. **Testing**: Add comprehensive tests for all new functionality

### Code Quality
- **Backend**: Python with flake8, black formatting
- **iOS**: SwiftUI with native error handling patterns
- **Database**: SQLAlchemy ORM with proper indexing
- **API**: FastAPI with Pydantic validation

## 📈 System Status

### ✅ Production Ready Components
- **Backend aggregation**: 35+ articles processed successfully
- **REST API server**: All endpoints functional with health monitoring
- **iOS application**: Clean UI, proper data display
- **Database operations**: Robust with reconnection handling
- **Test coverage**: 225/225 tests passing
- **Logging system**: Organized structure implemented

### 🚧 Future Enhancements
- **Android application**: Cross-platform mobile coverage
- **Push notifications**: Real-time article alerts
- **Offline support**: Local caching for mobile apps
- **Admin dashboard**: Web interface for content management
- **Analytics**: User engagement and content performance metrics

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch following naming conventions
3. **Implement** with comprehensive test coverage
4. **Test** all components: `python -m pytest`
5. **Document** changes in appropriate files
6. **Submit** pull request with detailed description

## 📄 License

MIT License - See LICENSE file for details.

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Documentation**: Check `docs/` directory for detailed guides
- **API Docs**: Available at `http://localhost:8000/docs` when server is running

---

**Latest Update**: v1.1.0 - Complete platform with backend services, REST API, iOS app, and comprehensive testing suite