import json
import logging
from typing import List, Dict

logging.basicConfig(
    filename="data/logs/feed_audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class FeedAuditor:
    """
    A class to manage and audit RSS feeds, including deduplication, validation,
    and blacklisting of problematic feeds.
    """

    def __init__(self, feeds_file: str, blacklist_file: str):
        """
        Initialize the FeedAuditor with feed and blacklist file paths.

        Args:
            feeds_file (str): Path to the feeds JSON file.
            blacklist_file (str): Path to the blacklist JSON file.
        """
        self.feeds_file = feeds_file
        self.blacklist_file = blacklist_file
        self.feeds = self._load_json(self.feeds_file)
        self.blacklist = self._load_json(self.blacklist_file)

    def _load_json(self, filepath: str) -> List[str]:
        """
        Load a JSON file and return its content.

        Args:
            filepath (str): Path to the JSON file.

        Returns:
            List[str]: Content of the JSON file or an empty list if not found.
        """
        try:
            with open(filepath, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logging.warning(f"{filepath} not found. Initializing with an empty list.")
            return []
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding {filepath}: {e}")
            return []

    def _save_json(self, data: List[str], filepath: str):
        """
        Save a list to a JSON file.

        Args:
            data (List[str]): Data to save.
            filepath (str): Path to the JSON file.
        """
        with open(filepath, "w") as file:
            json.dump(data, file, indent=4)

    def load_feeds(self):
        """
        Load RSS feeds dynamically from the feeds JSON file.

        Returns:
            List[str]: List of RSS feed URLs.
        """
        return self._load_json(self.feeds_file)

    def deduplicate_feeds(self):
        """
        Remove duplicate URLs from the feeds list.
        """
        original_count = len(self.feeds)
        self.feeds = list(set(self.feeds))
        self._save_json(self.feeds, self.feeds_file)
        logging.info(
            f"Deduplicated feeds. {original_count - len(self.feeds)} duplicates removed."
        )

    def validate_feeds(self):
        """
        Validate feeds against the blacklist and remove any blacklisted feeds.
        """
        original_count = len(self.feeds)
        self.feeds = [
            feed for feed in self.feeds if feed not in self.blacklist
        ]
        self._save_json(self.feeds, self.feeds_file)
        logging.info(
            f"Validated feeds. {original_count - len(self.feeds)} blacklisted feeds removed."
        )

    def blacklist_feed(self, feed_url: str):
        """
        Add a feed to the blacklist and remove it from the active feeds.

        Args:
            feed_url (str): The URL of the feed to blacklist.
        """
        if feed_url not in self.blacklist:
            self.blacklist.append(feed_url)
            self._save_json(self.blacklist, self.blacklist_file)
            logging.info(f"Blacklisted feed: {feed_url}")

        # Remove from active feeds
        if feed_url in self.feeds:
            self.feeds.remove(feed_url)
            self._save_json(self.feeds, self.feeds_file)

    def audit_feeds(self):
        """
        Perform a full audit of the feeds, including deduplication and validation.
        """
        logging.info("Starting feed audit.")
        self.deduplicate_feeds()
        self.validate_feeds()
        logging.info("Feed audit completed.")

    def find_duplicate_content_feeds(self, articles: Dict[str, List[str]]):
        """
        Identify feeds that consistently provide identical content and suggest blacklisting.

        Args:
            articles (Dict[str, List[str]]): A dictionary of feed URLs and their articles.

        Returns:
            List[str]: Feeds with duplicate content.
        """
        duplicate_feeds = []
        seen_content = {}

        for feed, content in articles.items():
            content_hash = hash(tuple(content))
            if content_hash in seen_content:
                duplicate_feeds.append(feed)
                logging.warning(
                    f"Duplicate content detected between {feed} and {seen_content[content_hash]}"
                )
            else:
                seen_content[content_hash] = feed

        return duplicate_feeds


# Example usage
if __name__ == "__main__":
    auditor = FeedAuditor(
        feeds_file="data/feeds.json", blacklist_file="data/blacklist.json"
    )
    feeds = auditor.load_feeds()
    print(f"Loaded feeds: {feeds}")
    auditor.audit_feeds()