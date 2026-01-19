import feedparser
import logging
from .base import BaseScraper
from datetime import datetime

logger = logging.getLogger(__name__)

class RSSScaper(BaseScraper):
    def scrape(self):
        articles = []
        try:
            logger.info(f"Fetching RSS feed: {self.name} - {self.url}")
            feed = feedparser.parse(self.url)
            
            if feed.bozo:
                logger.warning(f"RSS feed parsing warning for {self.name}: {feed.bozo_exception}")
            
            for entry in feed.entries[:20]:
                try:
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    author = entry.get('author', '')
                    
                    published = entry.get('published_parsed') or entry.get('updated_parsed')
                    if published:
                        published_date = datetime(*published[:6])
                    else:
                        published_date = datetime.now()
                    
                    if summary:
                        summary = self._clean_html(summary)
                    
                    article = self._create_article(
                        title=title,
                        url=link,
                        summary=summary,
                        author=author,
                        published_date=published_date
                    )
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error parsing RSS entry from {self.name}: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(articles)} articles from {self.name}")
            
        except Exception as e:
            logger.error(f"Error scraping RSS feed {self.name}: {e}")
        
        return articles
    
    def _clean_html(self, html_text):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text[:500] if len(text) > 500 else text
