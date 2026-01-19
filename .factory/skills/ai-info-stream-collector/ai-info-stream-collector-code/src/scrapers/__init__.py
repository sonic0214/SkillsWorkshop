from .rss_scraper import RSSScaper
from .web_scraper import WebScraper
from .api_scraper import APIScraper
from .base import BaseScraper, Article

def create_scraper(config):
    scraper_type = config.get('type', 'rss').lower()
    
    if scraper_type == 'rss':
        return RSSScaper(config)
    elif scraper_type == 'web':
        return WebScraper(config)
    elif scraper_type == 'api':
        return APIScraper(config)
    else:
        raise ValueError(f"Unknown scraper type: {scraper_type}")

__all__ = ['create_scraper', 'BaseScraper', 'Article', 'RSSScaper', 'WebScraper', 'APIScraper']
