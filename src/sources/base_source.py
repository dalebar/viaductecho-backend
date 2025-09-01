from abc import ABC, abstractmethod
from typing import List, Dict

class BaseNewsSource(ABC):
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    @abstractmethod
    def fetch_articles(self) -> List[Dict]:
        """Fetch and filter articles"""
        pass
    
    def filter_articles(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """Filter articles by keywords"""
        filtered = []
        for article in articles:
            title = article.get('original_title', '').lower()
            summary = article.get('original_summary', '').lower()
            
            if any(keyword in title or keyword in summary for keyword in keywords):
                filtered.append(article)
        
        return filtered