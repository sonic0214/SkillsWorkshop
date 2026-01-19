import requests
import logging
from .base import BaseScraper

logger = logging.getLogger(__name__)

class APIScraper(BaseScraper):
    def scrape(self):
        articles = []
        try:
            if self.name == "Hacker News":
                articles = self._scrape_hackernews()
            else:
                articles = self._scrape_generic()
            logger.info(f"Scraped {len(articles)} from {self.name}")
        except Exception as e:
            logger.error(f"Error scraping {self.name}: {e}")
        return articles
    
    def _scrape_hackernews(self):
        articles = []
        response = requests.get(self.url, timeout=30)
        story_ids = response.json()
        max_items = self.config.get('max_items', 8)
        for sid in story_ids[:max_items]:
            try:
                url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                data = requests.get(url, timeout=10).json()
                if data and data.get('type') == 'story':
                    articles.append(self._create_article(
                        title=data.get('title', 'No Title'),
                        url=data.get('url', f"https://news.ycombinator.com/item?id={sid}"),
                        author=data.get('by', '')
                    ))
            except:
                pass
        return articles
    
    def _scrape_generic(self):
        articles = []
        response = requests.get(self.url, timeout=30)
        data = response.json()
        items = data if isinstance(data, list) else data.get('articles', data.get('items', []))
        for item in items[:20]:
            articles.append(self._create_article(
                title=item.get('title', 'No Title'),
                url=item.get('url', item.get('link', '')),
                summary=item.get('description', item.get('summary', ''))
            ))
        return articles
