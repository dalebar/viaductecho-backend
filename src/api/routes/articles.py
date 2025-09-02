import math
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

try:
    from ...database.api_operations import APIOperations
except ImportError:
    from database.api_operations import APIOperations

from ..schemas.articles import (
    ArticleDetail,
    ArticleSummary,
    PaginatedArticles,
    PaginationInfo,
)
from ..schemas.common import ErrorResponse

router = APIRouter()


def get_db():
    """Dependency to get database operations instance"""
    db = APIOperations()
    try:
        yield db
    finally:
        db.close()


def create_pagination_info(page: int, per_page: int, total_items: int) -> PaginationInfo:
    """Create pagination information"""
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 0

    return PaginationInfo(
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


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
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
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
    hours: int = Query(24, ge=1, le=168, description="Hours back to look (max 168 = 1 week)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum articles to return"),
    db: APIOperations = Depends(get_db),
):
    """Get recent articles"""
    try:
        articles = db.get_recent_articles(hours=hours, limit=limit)

        return [
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
    query: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: APIOperations = Depends(get_db),
):
    """Search articles"""
    try:
        articles, total_count = db.search_articles(query=query, page=page, per_page=per_page)

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

        return ArticleDetail(
            id=article.id,
            title=article.original_title,
            link=article.original_link,
            summary=article.original_summary,
            source=article.original_source,
            source_type=article.source_type,
            published_date=article.original_pubdate,
            created_at=article.created_at,
            updated_at=article.updated_at,
            processed=article.processed,
            extracted_content=article.extracted_content,
            ai_summary=article.ai_summary,
            image_url=article.image_url,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve article: {str(e)}",
        )
