import yaml
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from .scrapers import create_scraper
from .translator import ArticleTranslator
from .storage import ArticleStorage

logger = logging.getLogger(__name__)

class ArticleCollector:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.storage = ArticleStorage(
            db_path=self.config['storage']['database'],
            json_path=self.config['storage']['output_file']
        )
        
        if self.config['translation']['enabled']:
            self.translator = ArticleTranslator()
        else:
            self.translator = None
        
        self.sources = self.config['sources']
    
    def collect_all(self, max_workers=5):
        logger.info(f"Starting collection from {len(self.sources)} sources")
        all_articles = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._collect_one, src): src 
                for src in self.sources
            }
            
            for future in as_completed(futures):
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                except Exception as e:
                    logger.error(f"Collection error: {e}")
        
        if self.translator:
            logger.info(f"Translating {len(all_articles)} articles")
            self._translate_all(all_articles)
        
        new_count = self.storage.save_articles(all_articles)
        stats = self.storage.get_stats()
        
        logger.info(f"Complete: {new_count} new, {stats['total_articles']} total")
        return new_count, stats
    
    def _collect_one(self, source_config):
        try:
            scraper = create_scraper(source_config)
            return scraper.scrape()
        except Exception as e:
            logger.error(f"Failed to scrape {source_config['name']}: {e}")
            return []
    
    def _translate_all(self, articles):
        for article in articles:
            try:
                if article.title:
                    article.title_cn = self.translator.translate(article.title)
                if article.summary and len(article.summary) < 1000:
                    article.summary_cn = self.translator.translate(article.summary)
            except Exception as e:
                logger.error(f"Translation error: {e}")
