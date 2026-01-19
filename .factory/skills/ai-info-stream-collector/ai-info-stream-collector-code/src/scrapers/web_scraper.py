import requests
from bs4 import BeautifulSoup
import logging
from .base import BaseScraper
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class WebScraper(BaseScraper):
    def scrape(self):
        articles = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if "huggingface" in self.url:
                articles = self._scrape_huggingface(soup)
            elif "paulgraham" in self.url:
                articles = self._scrape_paulgraham(soup)
            else:
                articles = self._scrape_generic(soup)
            
            logger.info(f"Scraped {len(articles)} from {self.name}")
        except Exception as e:
            logger.error(f"Error scraping {self.name}: {e}")
        return articles
    
    def _scrape_huggingface(self, soup):
        articles = []
        for paper in soup.find_all('article', limit=20):
            try:
                title_elem = paper.find('h3')
                if title_elem:
                    link = paper.find('a', href=True)
                    articles.append(self._create_article(
                        title=title_elem.get_text(strip=True),
                        url=f"https://huggingface.co{link['href']}" if link else ""
                    ))
            except:
                pass
        return articles
    
    def _scrape_paulgraham(self, soup):
        articles = []
        for link in soup.find_all('a', href=True, limit=20):
            if link['href'].endswith('.html'):
                articles.append(self._create_article(
                    title=link.get_text(strip=True),
                    url=f"https://paulgraham.com/{link['href']}"
                ))
        return articles[:10]
    
    def _scrape_generic(self, soup):
        articles = []
        elements = soup.find_all(['article', 'div'], class_=['post', 'article', 'item'], limit=20)
        for elem in elements:
            try:
                title_elem = elem.find(['h1', 'h2', 'h3'])
                link = elem.find('a', href=True)
                if title_elem and link:
                    articles.append(self._create_article(
                        title=title_elem.get_text(strip=True),
                        url=urljoin(self.url, link['href'])
                    ))
            except:
                pass
        return articles[:10]
