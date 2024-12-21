import feedparser
import concurrent.futures
from datetime import datetime
import requests
import logging
from pathlib import Path
import sqlite3
from queue import Queue
import threading
from newspaper import Article


# Set up logging
data_dir = Path(__file__).resolve().parent.parent / "data"
logs_dir = data_dir / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)  # Ensure the logs directory exists
log_file = logs_dir / "rss_helpers.log"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# File paths
db_path = data_dir / "rss_collector.db"

log_queue = Queue()


def log_to_database_batch_worker():
    """
    Worker to batch log messages into the database.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        while True:
            try:
                level, message = log_queue.get()
                if level is None and message is None:  # Exit signal
                    break
                cursor.execute(
                    """
                INSERT INTO logs (level, message)
                VALUES (?, ?)
                """,
                    (level, message),
                )
                conn.commit()
            except sqlite3.OperationalError as e:
                logging.error(f"Failed to log to database: {e}")
                conn.rollback()


log_thread = threading.Thread(target=log_to_database_batch_worker, daemon=True)
log_thread.start()


def log_to_database(level, message):
    """
    Add a log message to the queue for batched writing.
    """
    log_queue.put((level, message))


# Add this at the end of your program to shut down the logging thread
def shutdown_logging():
    log_queue.put((None, None))  # Send an exit signal
    log_thread.join()


def fetch_article_content(url):
    """
    Fetch the full content of an article using newspaper3k.
    """
    article = Article(url)
    try:
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logging.error(f"Failed to fetch article content from {url}: {e}")
        log_to_database("ERROR", f"Failed to fetch article content from {url}: {e}")
        return None
    
def fetch_feed(url):
    """
    Fetch a single RSS feed and return its entries as a list of dictionaries.
    """
    articles = []
    try:
        response = requests.get(url, timeout=10)  # Set timeout to 10 seconds
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        for entry in feed.entries:
            articles.append(
                {
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", "No Link"),
                    "published": entry.get("published", datetime.now().isoformat()),
                    "source": feed.feed.get("title", "Unknown Source"),
                }
            )
        logging.info(f"Fetched {len(articles)} articles from {url}.")
        log_to_database("INFO", f"Fetched {len(articles)} articles from {url}.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching feed {url}: {e}")
        log_to_database("ERROR", f"Error fetching feed {url}: {e}")
    return articles


def save_new_articles(articles, feed_urls, db_path=db_path):
    """
    Save new articles to the SQLite database and update feed URLs in the feeds table.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the database directory exists
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Ensure the articles table exists with a 'content' column
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                link TEXT UNIQUE,
                published TEXT,
                source TEXT,
                content TEXT
            )
            """
        )

        # Save articles with content
        for article in articles:
            content = fetch_article_content(article["link"])
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO articles (title, link, published, source, content)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        article["title"],
                        article["link"],
                        article["published"],
                        article["source"],
                        content,
                    ),
                )
                if cursor.rowcount > 0:
                    logging.info(f"New article added: {article['title']}")
                    log_to_database("INFO", f"New article added: {article['title']}")
                else:
                    logging.info(f"Duplicate article skipped: {article['link']}")
                    log_to_database("INFO", f"Duplicate article skipped: {article['link']}")
            except Exception as e:
                logging.error(f"Error saving article: {article['title']}, Error: {e}")
                log_to_database("ERROR", f"Error saving article: {article['title']}, Error: {e}")

        # Save feed URLs to the feeds table
        for url in feed_urls:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO feeds (url)
                    VALUES (?)
                    """,
                    (url,),
                )
                logging.info(f"Feed URL added or already exists: {url}")
                log_to_database("INFO", f"Feed URL added or already exists: {url}")
            except sqlite3.IntegrityError:
                logging.error(f"Error saving feed URL: {url}")
                log_to_database("ERROR", f"Error saving feed URL: {url}")

        conn.commit()


def fetch_all_feeds(feed_urls):
    """
    Fetch all RSS feeds in parallel and return a combined list of articles.
    """
    articles = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_feed, url): url for url in feed_urls}
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                articles.extend(future.result())
                logging.info(f"Successfully fetched feed: {url}")
                log_to_database("INFO", f"Successfully fetched feed: {url}")
            except Exception as e:
                logging.error(f"Error fetching feed {url}: {e}")
                log_to_database("ERROR", f"Error fetching feed {url}: {e}")
    return articles
