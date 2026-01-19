import json
import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ArticleStorage:
    def __init__(self, db_path='data/articles.db', json_path='data/articles.json'):
        self.db_path = db_path
        self.json_path = json_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                title_cn TEXT,
                url TEXT,
                source TEXT,
                category TEXT,
                published_date TEXT,
                summary TEXT,
                summary_cn TEXT,
                author TEXT,
                scraped_at TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON articles(source)')
        conn.commit()
        conn.close()

    def article_exists(self, article_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM articles WHERE id = ?', (article_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def save_articles(self, articles):
        new_count = 0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for article in articles:
            if not self.article_exists(article.id):
                d = article.to_dict()
                cursor.execute('''
                    INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (d['id'], d['title'], d.get('title_cn'), d['url'], d['source'],
                      d['category'], d['published_date'], d.get('summary'),
                      d.get('summary_cn'), d.get('author'), d['scraped_at']))
                new_count += 1

        conn.commit()
        conn.close()

        if new_count > 0:
            self._export_json()

        logger.info(f"Saved {new_count} new articles")
        return new_count

    def _export_json(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles ORDER BY scraped_at DESC')

        columns = [d[0] for d in cursor.description]
        articles = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(articles),
                'last_updated': datetime.now().isoformat(),
                'articles': articles
            }, f, ensure_ascii=False, indent=2)

    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM articles')
        total = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT source) FROM articles')
        sources = cursor.fetchone()[0]
        cursor.execute('SELECT source, COUNT(*) FROM articles GROUP BY source')
        by_source = dict(cursor.fetchall())
        conn.close()

        return {
            'total_articles': total,
            'total_sources': sources,
            'articles_by_source': by_source
        }
