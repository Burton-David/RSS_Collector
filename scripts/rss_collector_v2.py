import json
import time
import logging
from pathlib import Path
from rss_helpers import fetch_all_feeds, save_new_articles
import sqlite3

# Adjust paths for data files
data_dir = Path(__file__).resolve().parent.parent / "data"
feeds_file = data_dir / "feeds.json"
log_file = data_dir / "logs" / "rss_collector.log"
db_path = data_dir / "rss_collector.db"

# Configure file-based logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def log_to_database(level, message, db_path):
    """
    Save log messages to the logs table in the SQLite database.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Ensure the logs table exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            level TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """)
        cursor.execute("INSERT INTO logs (level, message) VALUES (?, ?)", (level, message))
        conn.commit()

if __name__ == "__main__":
    print("Starting RSS collection service...")

    # Load RSS feeds from the feeds.json file
    try:
        with open(feeds_file, "r") as file:
            feed_urls = json.load(file)  # Ensure this is a list of URLs
    except FileNotFoundError:
        error_msg = f"Error: {feeds_file} not found. Exiting."
        print(error_msg)
        logging.error(error_msg)
        log_to_database("ERROR", error_msg, db_path)
        exit(1)
    except json.JSONDecodeError as e:
        error_msg = f"Error decoding {feeds_file}: {e}. Exiting."
        print(error_msg)
        logging.error(error_msg)
        log_to_database("ERROR", error_msg, db_path)
        exit(1)

    try:
        while True:
            logging.info("Fetching RSS feeds...")
            log_to_database("INFO", "Fetching RSS feeds...", db_path)
            new_articles = fetch_all_feeds(feed_urls)
            save_new_articles(new_articles, feed_urls)
            logging.info("Waiting for the next fetch...")
            log_to_database("INFO", "Waiting for the next fetch...", db_path)
            time.sleep(180)  # Wait 3 minutes before fetching again
    except KeyboardInterrupt:
        print("\nRSS collection service stopped.")
        logging.info("RSS collection service stopped.")
        log_to_database("INFO", "RSS collection service stopped.", db_path)