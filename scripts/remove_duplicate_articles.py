import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).resolve().parent.parent / "data" / "rss_collector.db"

def remove_duplicate_articles():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM articles
            WHERE rowid NOT IN (
                SELECT MIN(rowid)
                FROM articles
                GROUP BY link
            )
        """)
        conn.commit()
        print("Duplicate articles removed.")

if __name__ == "__main__":
    remove_duplicate_articles()