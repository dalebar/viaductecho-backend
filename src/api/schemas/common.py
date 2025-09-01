from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_serializer


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Health status")
    total_articles: Optional[int] = Field(None, description="Total articles in database")
    recent_articles_24h: Optional[int] = Field(None, description="Articles added in last 24 hours")
    database_connected: bool = Field(..., description="Database connection status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class MessageResponse(BaseModel):
    """General message response"""

    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()