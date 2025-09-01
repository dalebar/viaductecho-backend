import hashlib
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import RSSArticle, Base
try:
    from ..config import Config
except ImportError:
    from config import Config
import logging

class DatabaseOperations:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logging.info("Database connection established")
    
    def article_exists(self, url: str) -> bool:
        """Check if article exists by URL hash"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        existing = self.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
        return existing is not None
    
    def insert_article(self, article_data: dict) -> RSSArticle:
        """Insert new article"""
        url_hash = hashlib.md5(article_data['original_link'].encode()).hexdigest()
        
        article = RSSArticle(
            original_title=article_data['original_title'],
            original_link=article_data['original_link'],
            original_summary=article_data.get('original_summary', ''),
            original_source=article_data['original_source'],
            source_type=article_data.get('source_type', 'RSS'),
            original_pubdate=article_data.get('original_pubdate'),
            url_hash=url_hash
        )
        
        self.session.add(article)
        self.session.commit()
        logging.info(f"Inserted article: {article.original_title}")
        return article
    
    def mark_processed(self, article_link: str):
        """Mark article as processed"""
        url_hash = hashlib.md5(article_link.encode()).hexdigest()
        article = self.session.query(RSSArticle).filter_by(url_hash=url_hash).first()
        if article:
            article.processed = True
            self.session.commit()
            logging.info(f"Marked processed: {article.original_title}")
    
    def close(self):
        self.session.close()