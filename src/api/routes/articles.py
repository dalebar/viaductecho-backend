from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

try:
    from ...database.api_operations import APIOperations
except ImportError:
    from database.api_operations import APIOperations
try:
    from ...config import Config
except ImportError:
    from config import Config

from ..schemas.articles import (
    ArticleDetail,
    ArticleSummary,
    PaginatedArticles,
    PaginationInfo,
)
from ..schemas.common import ErrorResponse
from ..utils.mappers import create_pagination_info as _create_pagination_info
from ..utils.mappers import to_article_detail, to_article_summary

router = APIRouter()


def get_db():
    """Dependency to get database operations instance"""
    db = APIOperations()
    try:
        yield db
    finally:
        db.close()


def create_pagination_info(
    page: int, per_page: int, total_items: int
) -> PaginationInfo:
    # Keep function for backward-compatibility import paths, delegate to util
    return _create_pagination_info(page, per_page, total_items)


@router.get(
    "/articles",
    response_model=PaginatedArticles,
    summary="Get Articles",
    description="Get paginated list of articles with optional filtering",
    responses={
        200: {"description": "Articles retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        Config.DEFAULT_PAGE_SIZE,
        ge=1,
        le=Config.MAX_PAGE_SIZE,
        description="Items per page",
    ),
    source: str = Query(None, description="Filter by source name"),
    processed_only: bool = Query(True, description="Only return processed articles"),
    db: APIOperations = Depends(get_db),
):
    """Get paginated articles"""
    try:
        articles, total_count = db.get_articles_paginated(
            page=page, per_page=per_page, source=source, processed_only=processed_only
        )

        # Convert to response models
        article_summaries = [to_article_summary(article) for article in articles]

        pagination = create_pagination_info(page, per_page, total_count)

        return PaginatedArticles(articles=article_summaries, pagination=pagination)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve articles: {str(e)}",
        )


@router.get(
    "/articles/recent",
    response_model=List[ArticleSummary],
    summary="Get Recent Articles",
    description="Get articles from the last N hours",
    responses={
        200: {"description": "Recent articles retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_recent_articles(
    hours: int = Query(
        24, ge=1, le=168, description="Hours back to look (max 168 = 1 week)"
    ),
    limit: int = Query(
        50, ge=1, le=Config.MAX_PAGE_SIZE, description="Maximum articles to return"
    ),
    db: APIOperations = Depends(get_db),
):
    """Get recent articles"""
    try:
        articles = db.get_recent_articles(hours=hours, limit=limit)

        return [to_article_summary(article) for article in articles]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent articles: {str(e)}",
        )


@router.get(
    "/articles/search",
    response_model=PaginatedArticles,
    summary="Search Articles",
    description="Search articles by title, summary, or content",
    responses={
        200: {"description": "Search completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid search parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def search_articles(
    query: str = Query(
        ..., min_length=2, description="Search query (minimum 2 characters)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        Config.DEFAULT_PAGE_SIZE,
        ge=1,
        le=Config.MAX_PAGE_SIZE,
        description="Items per page",
    ),
    db: APIOperations = Depends(get_db),
):
    """Search articles"""
    try:
        articles, total_count = db.search_articles(
            query=query, page=page, per_page=per_page
        )

        # Convert to response models
        article_summaries = [
            ArticleSummary(
                id=article.id,
                title=article.original_title,
                link=article.original_link,
                summary=article.original_summary,
                source=article.original_source,
                source_type=article.source_type,
                published_date=article.original_pubdate,
                created_at=article.created_at,
                image_url=article.image_url,
            )
            for article in articles
        ]

        pagination = create_pagination_info(page, per_page, total_count)

        return PaginatedArticles(articles=article_summaries, pagination=pagination)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get(
    "/articles/{article_id}",
    response_model=ArticleDetail,
    summary="Get Article",
    description="Get detailed information about a specific article",
    responses={
        200: {"description": "Article retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Article not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_article(article_id: int, db: APIOperations = Depends(get_db)):
    """Get single article by ID"""
    try:
        article = db.get_article_by_id(article_id)

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with ID {article_id} not found",
            )

        return to_article_detail(article)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve article: {str(e)}",
        )
