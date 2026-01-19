from abc import ABC, abstractmethod
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)

class Article:
    def __init__(self, title, url, source, published_date=None, summary=None, author=None, category=None):
        self.title = title
        self.url = url
        self.source = source
        self.published_date = published_date or datetime.now()
        self.summary = summary
        self.author = author
        self.category = category
        self.id = self._generate_id()
        self.title_cn = None
        self.summary_cn = None
        self.scraped_at = datetime.now()
    
    def _generate_id(self):
        unique_string = f"{self.source}_{self.url}_{self.title}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'title_cn': self.title_cn,
            'url': self.url,
            'source': self.source,
            'category': self.category,
            'published_date': self.published_date.isoformat() if isinstance(self.published_date, datetime) else str(self.published_date),
            'summary': self.summary,
            'summary_cn': self.summary_cn,
            'author': self.author,
            'scraped_at': self.scraped_at.isoformat()
        }

class BaseScraper(ABC):
    def __init__(self, config):
        self.name = config.get('name')
        self.url = config.get('url')
        self.category = config.get('category')
        self.config = config
    
    @abstractmethod
    def scrape(self):
        pass
    
    def _create_article(self, title, url, **kwargs):
        return Article(
            title=title,
            url=url,
            source=self.name,
            category=self.category,
            **kwargs
        )
