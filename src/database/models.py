from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RSSArticle(Base):
    __tablename__ = 'rss_articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_title = Column(String(500), nullable=False)
    original_link = Column(Text, nullable=False, unique=True)
    original_summary = Column(Text)
    original_source = Column(String(100), nullable=False)
    source_type = Column(String(50))
    original_pubdate = Column(DateTime(timezone=True))
    url_hash = Column(String(64), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)