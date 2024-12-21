# RSS Collector

This project aims to develop a powerful, scalable, and modular RSS feed collection and processing system, capable of collecting articles from various RSS feeds, analyzing them, and storing the results in a structured SQLite database.

## Project Structure

RSS_Collector/
├── data/
│   ├── feeds.json
│   ├── logs/
│   │   └── rss_collector.log
│   ├── rss_articles.csv (if applicable)
│   ├── rss_collector.db
├── scripts/
│   ├── init.py
│   ├── article_analyzer.py
│   ├── association_rules.py
│   ├── database_manager.py
│   ├── feed_auditor.py
│   ├── rss_collector_v2.py
│   ├── rss_helpers.py
│   ├── utils.py
├── README.md

## Features

1. **RSS Feed Collection**:
   - Fetch articles from RSS feeds.
   - Store feed URLs and articles in an SQLite database.

2. **Feed Auditing**:
   - Identify and remove duplicate or problematic feeds.
   - Prevent blacklisted feeds from being re-added.

3. **Data Storage**:
   - Store articles, feeds, and logs in structured SQLite tables.

4. **Content Scraping**:
   - Use `newspaper3k` to fetch and store full article content.

5. **Data Analysis**:
   - Analyze articles using `association_rules.py` for trends and relationships.

6. **Error Logging**:
   - Record errors and events in the `logs` table and log files.

## Setup Instructions

### Prerequisites
1. Install Python 3.10 or above.
2. Create a virtual environment:
   ```bash
   python3 -m venv article_env
   source article_env/bin/activate  # On Windows: article_env\Scripts\activate

	3.	Install dependencies:

pip install -r requirements.txt



Required Python Libraries
	•	feedparser
	•	sqlite3
	•	requests
	•	concurrent.futures
	•	newspaper3k
	•	lxml

Initial Setup
	1.	Create the SQLite database structure:

python3 scripts/database_manager.py


	2.	Add RSS feeds to data/feeds.json:

[
    "https://rss.cnn.com/rss/edition.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
]


	3.	Run the main RSS collector script:

python3 scripts/rss_collector_v2.py



Usage

Starting the RSS Collector

Run the RSS collector script to start fetching articles:

python3 scripts/rss_collector_v2.py

Checking Database Status

Inspect the database using db_status_checker.py:

python3 scripts/db_status_checker.py

Feed Auditing

Audit RSS feeds to remove duplicates and blacklist problematic sources:

python3 scripts/feed_auditor.py

Data Analysis

Run association rules analysis on the stored articles:

python3 scripts/association_rules.py

Development Roadmap
	•	Create a modular project structure.
	•	Implement RSS feed collection.
	•	Store articles in SQLite database.
	•	Add feed auditing functionality.
	•	Scrape full article content using newspaper3k.
	•	Add comprehensive logging for errors and events.
	•	Integrate advanced data analysis tools.
	•	Implement cloud storage and processing using GCP.
	•	Develop a web interface for querying and displaying results.

To-Do List

Current Priorities
	•	Verify data integrity in the database.
	•	Enhance logging system for better debugging.
	•	Test article content scraping for accuracy.

Future Features
	•	Scale the system for handling thousands of feeds.
	•	Add real-time notification system for important articles.
	•	Integrate machine learning for trend detection and insights.

Contact

For questions or contributions, feel free to reach out at [Your Email Address].

This project is actively being developed. Contributions are welcome!

Let me know if there's anything else you'd like to add or modify!