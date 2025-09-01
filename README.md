# Viaduct Echo

A Python-based news aggregation system that monitors local news sources for Greater Manchester area content, processes articles using AI summarization, and publishes curated content to a Jekyll-based website via GitHub Pages.

## Overview

Viaduct Echo automatically:
- Fetches articles from multiple news sources (BBC Manchester, Manchester Evening News, Stockport Nub News)
- Filters content for local relevance using configurable keywords
- Extracts full article content from source websites
- Generates AI-powered summaries using OpenAI's GPT models
- Creates engaging images for articles
- Publishes formatted posts to GitHub Pages via Jekyll

## Features

- **Multi-source aggregation**: RSS feeds and web scraping
- **Intelligent filtering**: Keyword-based relevance detection
- **AI-powered processing**: Article summarization and image generation
- **Automated publishing**: Direct integration with GitHub Pages
- **Robust error handling**: Comprehensive logging and graceful failure recovery
- **Rate limiting**: Respectful scraping with built-in delays
- **Duplicate detection**: Prevents republishing of existing content

## Architecture

```
src/
├── main.py              # Main application and scheduler
├── config.py            # Configuration and environment variables
├── database/
│   ├── models.py        # SQLAlchemy database models
│   └── operations.py    # Database CRUD operations
├── sources/             # News source implementations
│   ├── base_source.py   # Abstract base class for sources
│   ├── bbc_source.py    # BBC Manchester RSS feed
│   ├── men_source.py    # Manchester Evening News RSS feed
│   └── nub_source.py    # Stockport Nub News web scraper
├── processors/          # Content processing modules
│   ├── content_extractor.py  # Full article content extraction
│   └── ai_summarizer.py      # OpenAI-powered summarization
└── publishers/
    └── github_publisher.py   # GitHub Pages publishing
```

## Prerequisites

- Python 3.11+
- PostgreSQL database (Neon recommended)
- OpenAI API key
- GitHub personal access token
- GitHub repository for Jekyll site

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd viaductecho-backend
   ```

2. **Install dependencies** (using uv):
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
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

4. **Initialize the database**:
   ```bash
   python -c "from src.database.operations import DatabaseOperations; DatabaseOperations().create_tables()"
   ```

## Configuration

### Keywords
The system filters articles based on keywords defined in `src/config.py`. Current keywords target Greater Manchester area:

```python
KEYWORDS = [
    'stockport', 'manchester', 'macclesfield', 'wilmslow', 'altrincham',
    'sale', 'urmston', 'stretford', 'chorlton', 'didsbury', 'burnage',
    'levenshulme', 'longsight', 'fallowfield', 'withington', 'wythenshawe',
    'oldham', 'rochdale', 'bury', 'bolton', 'salford', 'eccles', 'swinton',
    'worsley', 'walkden', 'farnworth', 'little lever', 'kearsley',
    'prestwich', 'whitefield', 'radcliffe', 'ramsbottom', 'tottington',
    'heywood', 'middleton', 'chadderton', 'shaw', 'royton', 'lees',
    'mossley', 'stalybridge', 'hyde', 'denton', 'audenshaw', 'dukinfield',
    'ashton-under-lyne', 'droylsden', 'failsworth', 'moston', 'blackley',
    'crumpsall', 'cheetham hill', 'higher blackley', 'harpurhey',
    'collyhurst', 'newton heath', 'clayton', 'openshaw', 'gorton',
    'belle vue', 'reddish', 'bredbury', 'marple', 'poynton', 'bollington',
    'knutsford', 'northwich', 'winsford', 'middlewich', 'sandbach',
    'crewe', 'nantwich', 'congleton', 'buxton', 'glossop', 'hadfield',
    'new mills', 'whaley bridge', 'chapel-en-le-frith', 'high peak'
]
```

### News Sources
- **BBC Manchester**: `http://feeds.bbci.co.uk/news/england/manchester/rss.xml`
- **Manchester Evening News**: `https://www.manchestereveningnews.co.uk/news/greater-manchester-news/?service=rss`
- **Stockport Nub News**: `https://stockport.nub.news/news` (web scraping)

## Usage

### Run Once
```bash
python src/main.py
```

### Run with Scheduling
The main application includes APScheduler for automated execution:
- Runs every 2 hours during daytime (8 AM - 10 PM)
- Configurable via cron expression in `src/main.py`

### Manual Testing

**Test database connection**:
```bash
python tests/test_db.py
```

**Run specific source**:
```python
from src.sources.bbc_source import BBCSource
source = BBCSource()
articles = source.fetch_articles()
print(f"Found {len(articles)} articles")
```

**Test AI summarization**:
```python
from src.processors.ai_summarizer import AISummarizer
summarizer = AISummarizer()
summary = summarizer.generate_summary("Article content here...")
```

## Testing

Comprehensive test suite with 95+ tests covering all components:

```bash
# Run all tests
python -m pytest

# Run specific test files
python -m pytest tests/test_bbc_source.py -v
python -m pytest tests/test_men_source.py -v  
python -m pytest tests/test_nub_source.py -v

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

### Test Coverage
- **DatabaseOperations**: 12 tests - CRUD operations, duplicate detection
- **AISummarizer**: 14 tests - OpenAI integration, error handling
- **ContentExtractor**: 20 tests - Web scraping, source-specific parsers
- **GitHubPublisher**: 14 tests - Jekyll publishing, GitHub API
- **BaseNewsSource**: 21 tests - Abstract base class functionality
- **BBCSource**: 17 tests - RSS feed parsing, keyword filtering
- **MENSource**: 17 tests - Manchester Evening News RSS processing
- **NubSource**: 19 tests - Web scraping, JSON-LD extraction

## Development

### Adding New News Sources

1. Create a new source class inheriting from `BaseNewsSource`:
```python
from .base_source import BaseNewsSource

class NewSource(BaseNewsSource):
    def __init__(self):
        super().__init__("Source Name")
        
    def fetch_articles(self) -> List[Dict]:
        # Implementation here
        pass
```

2. Add comprehensive tests following existing patterns
3. Update `src/main.py` to include the new source

### Modifying Content Processing

Content processors are modular and can be extended:
- **ContentExtractor**: Add new source-specific parsers
- **AISummarizer**: Modify prompts or add new AI providers

### Database Schema

The system uses a single table `rss_articles`:
```sql
CREATE TABLE rss_articles (
    id SERIAL PRIMARY KEY,
    original_title TEXT NOT NULL,
    original_link TEXT UNIQUE NOT NULL,
    original_summary TEXT,
    original_source TEXT NOT NULL,
    source_type TEXT NOT NULL,
    original_pubdate TIMESTAMP,
    extracted_content TEXT,
    ai_summary TEXT,
    ai_image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Monitoring and Logging

The application provides comprehensive logging:
- **INFO**: Successful operations, article counts
- **ERROR**: Failures with detailed context
- **WARNING**: Rate limiting, retries

Logs are output to stdout and can be redirected:
```bash
python src/main.py >> viaduct-echo.log 2>&1
```

## Production Deployment

### Environment Setup
1. Use environment variables for all sensitive configuration
2. Set up proper database connection pooling
3. Configure log rotation
4. Monitor API usage limits (OpenAI, GitHub)

### Scheduling Options
- **Cron**: `0 */2 8-22 * * *` (every 2 hours, 8 AM - 10 PM)
- **systemd**: Create service unit for automatic startup
- **Docker**: Container deployment with volume mounts for persistence

### Rate Limiting Considerations
- OpenAI: Monitor token usage and costs
- GitHub API: 5000 requests/hour for authenticated users
- News sources: Built-in delays (2 seconds for web scraping)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests for new functionality
4. Ensure all tests pass: `python -m pytest`
5. Submit a pull request with detailed description

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or contributions, please:
1. Check existing issues in the repository
2. Create detailed bug reports with logs and reproduction steps
3. Include relevant system information (Python version, OS, etc.)

## Changelog

### v1.0.0
- Initial release
- Multi-source news aggregation
- AI-powered content processing
- GitHub Pages publishing
- Comprehensive test suite
- Rate limiting and error handling
