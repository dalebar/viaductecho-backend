from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer


class SourceStats(BaseModel):
    """Source statistics"""

    name: str = Field(..., description="Source name")
    article_count: int = Field(..., description="Total articles from this source", ge=0)
    processed_count: int = Field(..., description="Processed articles from this source", ge=0)
    latest_article: Optional[datetime] = Field(None, description="Date of latest article")

    @field_serializer("latest_article")
    def serialize_latest_article(self, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None


class SourcesResponse(BaseModel):
    """Response containing all sources with statistics"""

    sources: List[SourceStats] = Field(..., description="List of sources with statistics")
    total_sources: int = Field(..., description="Total number of sources", ge=0)
