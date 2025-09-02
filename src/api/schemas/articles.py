from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ArticleBase(BaseModel):
    """Base article schema"""

    title: str = Field(..., description="Article title")
    link: str = Field(..., description="Original article URL")
    summary: Optional[str] = Field(None, description="Article summary")
    source: str = Field(..., description="Source name")
    source_type: Optional[str] = Field(None, description="Type of source (RSS, Web scraping)")
    published_date: Optional[datetime] = Field(None, description="Original publication date")

    @field_serializer("published_date")
    def serialize_published_date(self, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None


class ArticleSummary(ArticleBase):
    """Article summary for list views"""

    id: int = Field(..., description="Article ID")
    created_at: datetime = Field(..., description="Date added to system")
    image_url: Optional[str] = Field(None, description="Article image URL")

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()


class ArticleDetail(ArticleBase):
    """Detailed article with full content"""

    id: int = Field(..., description="Article ID")
    created_at: datetime = Field(..., description="Date added to system")
    updated_at: Optional[datetime] = Field(None, description="Last updated date")
    processed: bool = Field(..., description="Whether article has been processed")
    extracted_content: Optional[str] = Field(None, description="Extracted article content")
    ai_summary: Optional[str] = Field(None, description="AI-generated summary")
    image_url: Optional[str] = Field(None, description="Article image URL")

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()

    @field_serializer("updated_at")
    def serialize_updated_at(self, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None


class PaginationInfo(BaseModel):
    """Pagination metadata"""

    page: int = Field(..., description="Current page number", ge=1)
    per_page: int = Field(..., description="Items per page", ge=1, le=100)
    total_items: int = Field(..., description="Total number of items", ge=0)
    total_pages: int = Field(..., description="Total number of pages", ge=0)
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class PaginatedArticles(BaseModel):
    """Paginated article response"""

    articles: List[ArticleSummary] = Field(..., description="List of articles")
    pagination: PaginationInfo = Field(..., description="Pagination information")


class ArticleSearchParams(BaseModel):
    """Article search parameters"""

    query: str = Field(..., description="Search query", min_length=2)
    page: int = Field(1, description="Page number", ge=1)
    per_page: int = Field(20, description="Items per page", ge=1, le=100)


class ArticleListParams(BaseModel):
    """Article list parameters"""

    page: int = Field(1, description="Page number", ge=1)
    per_page: int = Field(20, description="Items per page", ge=1, le=100)
    source: Optional[str] = Field(None, description="Filter by source")
    processed_only: bool = Field(True, description="Only return processed articles")


class RecentArticlesParams(BaseModel):
    """Recent articles parameters"""

    hours: int = Field(24, description="Hours back to look", ge=1, le=168)  # Max 1 week
    limit: int = Field(50, description="Maximum articles to return", ge=1, le=100)
