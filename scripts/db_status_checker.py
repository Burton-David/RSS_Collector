import sqlite3
from pathlib import Path

# Define the database path
db_path = Path(__file__).resolve().parent.parent / "data" / "rss_collector.db"

def check_table_counts(cursor):
    """
    Check the number of rows in each table.
    """
    print("\nTable Counts:")
    tables = ['articles', 'feeds', 'logs']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f" - {table}: {count} rows")

def check_recent_articles(cursor, limit=5):
    """
    Display the most recent articles.
    """
    print("\nMost Recent Articles:")
    cursor.execute("""
        SELECT title, published, source 
        FROM articles 
        ORDER BY published DESC 
        LIMIT ?;
    """, (limit,))
    articles = cursor.fetchall()
    for article in articles:
        print(f" - Title: {article[0]}\n   Published: {article[1]}\n   Source: {article[2]}")

def check_feed_urls(cursor, limit=5):
    """
    Display feed URLs.
    """
    print("\nFeed URLs:")
    cursor.execute("""
        SELECT url, added_on 
        FROM feeds 
        ORDER BY added_on DESC 
        LIMIT ?;
    """, (limit,))
    feeds = cursor.fetchall()
    for feed in feeds:
        print(f" - URL: {feed[0]}\n   Added On: {feed[1]}")

def check_logs(cursor, limit=5):
    """
    Display recent logs.
    """
    print("\nRecent Logs:")
    cursor.execute("""
        SELECT timestamp, level, message 
        FROM logs 
        ORDER BY timestamp DESC 
        LIMIT ?;
    """, (limit,))
    logs = cursor.fetchall()
    for log in logs:
        print(f" - Time: {log[0]}\n   Level: {log[1]}\n   Message: {log[2]}")

def detailed_database_inspection():
    """
    Perform a detailed inspection of the database.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            print(f"Inspecting database: {db_path}")
            
            # Check table counts
            check_table_counts(cursor)
            
            # Check recent articles
            check_recent_articles(cursor)
            
            # Check feed URLs
            check_feed_urls(cursor)
            
            # Check logs
            check_logs(cursor)
            
            print("\nDatabase inspection completed successfully.")
    except sqlite3.Error as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    detailed_database_inspection()