# Session Notes - News Dashboard Development

**Branch:** `news`
**Date:** 2025-12-03
**Focus:** Fix AI summary bug + Build news management dashboard

---

## 🐛 AI Summary Bug - Root Cause Analysis

### Symptoms
- ~25% of articles getting bad AI summaries
- ChatGPT responds: "It seems there's no text provided for summarisation..."
- **Only affects Manchester Evening News (MEN) source**

### Root Cause: Content Extractor Failure ✅
The AI is working fine. The problem is `extracted_content` is **EMPTY** in the database for affected articles.

### Affected Article Patterns

1. **"Top stories you may have missed" articles**
   - Title pattern: `Top <LOCATION> stories you may have missed this week`
   - Content: Multiple mini-stories, each with "READ IN FULL HERE" links
   - Truncated/aggregated content
   - **Solution:** Filter these out entirely during aggregation

2. **"What you need to know about..." articles**
   - Bullet-pointed paragraphs
   - MEN content extractor fails to parse properly
   - **Solution:** Improve MEN scraper to handle bullet lists

### Evidence
```
2025-12-01 15:00:04,000 - INFO - Updated content for: What you need to know...
2025-12-01 15:00:06,454 - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2025-12-01 15:00:06,455 - INFO - AI summary generated
```
Extraction claims success, but database shows `extracted_content` is empty.

---

## 🎯 Next Session Roadmap

### Phase 1: Fix Content Extraction (Priority 1)
**File:** `src/processors/content_extractor.py`

1. **Add title-based filtering:**
   - Skip articles with title containing "Top * stories * missed"
   - Add to `Config.EXCLUDED_PATTERNS` or filter in source

2. **Improve MEN content extractor:**
   - Handle bullet-point articles (`<ul>`, `<li>` tags)
   - Handle "What you need to know" article structure
   - Debug why extraction returns empty for certain layouts

3. **Add validation before AI summarization:**
   ```python
   if not extracted_content or len(extracted_content.strip()) < 100:
       logger.warning(f"Content too short, skipping AI summary: {article.title}")
       # Don't call OpenAI, mark as failed, or use original summary
   ```

### Phase 2: News Dashboard - Admin CRUD (Priority 2)
**Files to create/modify:**
- `src/api/schemas/news.py` - Pydantic schemas (ArticleCreate, ArticleUpdate, ArticleDetail)
- `src/api/routes/news.py` - Public news API endpoints (GET /articles, GET /articles/:slug)
- `src/api/routes/admin.py` - Admin endpoints (POST, PATCH, DELETE articles)
- `src/api/static/admin.html` - Add "News Articles" tab

**Features:**
- List all news articles (with status: draft/published)
- Edit article: title, content, AI summary, image URL
- Delete article (soft delete?)
- Manual article creation with "Manual" source
- Regenerate Jekyll post after edits

### Phase 3: Manual Article Creation (Priority 3)
- "Create New Article" form in admin
- Image upload for news articles
- Source name: "Manual"
- Draft → Publish workflow

### Phase 4: New News Sources (If time allows)
**Candidates:**
- https://www.onestockport.co.uk/news/
- https://totallystockport.co.uk/latest-news/
- https://www.stockport.gov.uk/landing/news-media

**Approach:**
1. Check for RSS feeds first (easiest)
2. Use Playwright/Selenium for JavaScript-rendered sites
3. Follow `BaseNewsSource` pattern

---

## 📁 Key Files

### Current News System
- `src/main.py` - ViaductEcho class, scheduler (runs hourly 5 AM - 8 PM)
- `src/sources/` - News source scrapers (BBC, MEN, Nub)
- `src/processors/content_extractor.py` - Extracts article content (NEEDS FIX)
- `src/processors/ai_summarizer.py` - OpenAI integration (working fine)
- `src/publishers/github_publisher.py` - Publishes Jekyll posts
- `src/database/models.py` - `RSSArticle` model
- `src/database/operations.py` - Database operations

### Logs
- `logs/scheduler.log` - Main scheduler logs
- `logs/sessions/*` - Detailed session logs
- `logs/api.log` - API logs

---

## 🔧 Technical Decisions

### Article Status System
- **draft:** Not published to Jekyll yet
- **published:** Live on GitHub Pages
- **deleted:** Soft delete (keep in DB, don't publish)

### Manual Articles
- `source_name`: "Manual"
- `source_type`: "manual"
- `source_url`: NULL

### Content Fields (what's editable)
1. `original_title` / `title`
2. `extracted_content` (full article text)
3. `ai_summary` (summary for Jekyll)
4. `image_url`
5. `status` (draft/published/deleted)

---

## 💡 Key Insights

1. **MEN content extractor is fragile** - Needs robust handling of different article layouts
2. **Empty content = bad AI summary** - Always validate before sending to OpenAI
3. **Some article types should be filtered** - Not all RSS items are suitable
4. **News dashboard mirrors events structure** - Can reuse patterns from events admin
5. **User wants full editorial control** - Manual creation, editing both content AND summaries

---

## 🚀 Ready for Next Session

- [x] `news` branch created and pushed
- [x] Root cause identified (content extraction, not AI)
- [x] Clear roadmap established
- [x] User preferences documented
- [x] Open to complexity (Playwright/Selenium)
- [x] Open-ended timeline - focus on quality

**Branch:** `news`
**Next steps:** Start with fixing content extraction, then build news admin dashboard.
