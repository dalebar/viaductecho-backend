from fastapi import APIRouter, Depends, HTTPException, Query, status

try:
    from ...database.api_operations import APIOperations
except ImportError:
    from database.api_operations import APIOperations
try:
    from ...config import Config
except ImportError:
    from config import Config

from ..schemas.articles import PaginatedArticles
from ..schemas.common import ErrorResponse
from ..schemas.sources import SourcesResponse, SourceStats
from ..utils.mappers import create_pagination_info, to_article_summary

router = APIRouter()


def get_db():
    """Dependency to get database operations instance"""
    db = APIOperations()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/sources",
    response_model=SourcesResponse,
    summary="Get Sources",
    description="Get all news sources with statistics",
    responses={
        200: {"description": "Sources retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_sources(db: APIOperations = Depends(get_db)):
    """Get all sources with statistics"""
    try:
        sources_data = db.get_sources_with_stats()

        sources = [
            SourceStats(
                name=source["name"],
                article_count=source["article_count"],
                processed_count=source["processed_count"],
                latest_article=source["latest_article"],
            )
            for source in sources_data
        ]

        return SourcesResponse(sources=sources, total_sources=len(sources))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sources: {str(e)}",
        )


@router.get(
    "/sources/{source_name}/articles",
    response_model=PaginatedArticles,
    summary="Get Articles by Source",
    description="Get paginated articles from a specific source",
    responses={
        200: {"description": "Articles retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        404: {"model": ErrorResponse, "description": "Source not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_articles_by_source(
    source_name: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        Config.DEFAULT_PAGE_SIZE,
        ge=1,
        le=Config.MAX_PAGE_SIZE,
        description="Items per page",
    ),
    db: APIOperations = Depends(get_db),
):
    """Get articles from a specific source"""
    try:
        # First check if source exists by getting all sources
        sources_data = db.get_sources_with_stats()
        source_names = [source["name"] for source in sources_data]

        if source_name not in source_names:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source '{source_name}' not found",
            )

        articles, total_count = db.get_articles_by_source(
            source=source_name, page=page, per_page=per_page
        )

        # Convert to response models
        article_summaries = [to_article_summary(article) for article in articles]

        pagination = create_pagination_info(page, per_page, total_count)

        return PaginatedArticles(articles=article_summaries, pagination=pagination)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve articles from source '{source_name}': {str(e)}",
        )
