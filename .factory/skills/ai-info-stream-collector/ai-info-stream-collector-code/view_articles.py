#!/usr/bin/env python3
import sqlite3
import sys

db_path = '/Users/admin/KnowledgeSystem/60-69 兴趣·爱好/61 咨询/61.01 AI信息流/articles.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

if '--stats' in sys.argv:
    cursor.execute('SELECT COUNT(*) FROM articles')
    print(f"Total articles: {cursor.fetchone()[0]}")

    cursor.execute('SELECT source, COUNT(*) as count FROM articles GROUP BY source ORDER BY count DESC')
    print("\nArticles by source:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    cursor.execute('SELECT category, COUNT(*) as count FROM articles GROUP BY category ORDER BY count DESC')
    print("\nArticles by category:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

elif '--latest' in sys.argv:
    limit = int(sys.argv[sys.argv.index('--latest') + 1]) if len(sys.argv) > sys.argv.index('--latest') + 1 else 10
    cursor.execute('SELECT title, title_cn, source, url, scraped_at FROM articles ORDER BY scraped_at DESC LIMIT ?', (limit,))
    print(f"Latest {limit} articles:\n")
    for row in cursor.fetchall():
        title = row[1] if row[1] else row[0]
        print(f"[{row[2]}] {title}")
        print(f"  URL: {row[3]}")
        print(f"  Time: {row[4]}\n")

else:
    print("Usage:")
    print("  python3 view_articles.py --stats              Show statistics")
    print("  python3 view_articles.py --latest [N]         Show latest N articles (default 10)")

conn.close()
