import sqlite3
from pathlib import Path
from collections import Counter

# Database path
db_path = Path(__file__).resolve().parent.parent / "data" / "rss_collector.db"

def verify_data_integrity():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Check for duplicate articles
        cursor.execute("""
            SELECT title, COUNT(*) AS cnt
            FROM articles
            GROUP BY title
            HAVING cnt > 1
        """)
        duplicates = cursor.fetchall()

        # Check for missing data in articles
        cursor.execute("""
            SELECT id, title, link, source
            FROM articles
            WHERE title IS NULL OR link IS NULL OR source IS NULL
        """)
        incomplete_articles = cursor.fetchall()

        # Check for duplicate feeds
        cursor.execute("""
            SELECT url, COUNT(*) AS cnt
            FROM feeds
            GROUP BY url
            HAVING cnt > 1
        """)
        duplicate_feeds = cursor.fetchall()

        # Output results
        print("Data Integrity Report")
        print("======================")
        print(f"Total duplicate articles: {len(duplicates)}")
        if duplicates:
            print("Sample duplicates:")
            for title, count in duplicates[:5]:
                print(f" - {title} (count: {count})")

        print(f"\nTotal incomplete articles: {len(incomplete_articles)}")
        if incomplete_articles:
            print("Sample incomplete articles:")
            for id_, title, link, source in incomplete_articles[:5]:
                print(f" - ID: {id_}, Title: {title}, Link: {link}, Source: {source}")

        print(f"\nTotal duplicate feeds: {len(duplicate_feeds)}")
        if duplicate_feeds:
            print("Sample duplicate feeds:")
            for url, count in duplicate_feeds[:5]:
                print(f" - {url} (count: {count})")

if __name__ == "__main__":
    verify_data_integrity()