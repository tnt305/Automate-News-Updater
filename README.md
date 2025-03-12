Automatic Scraper

Overview

This automatic scraper is designed to collect and aggregate the latest news and job postings from multiple sources, providing an up-to-date feed of information related to AI and technology trends. The scraper supports the following sources:

GitHub – Fetching and aggregating the latest news from GitHub.

LinkedIn – Fetching and aggregating the latest news from LinkedIn.

Twitter – Fetching and aggregating the latest news from Twitter.

AI Job Listings – Fetching and aggregating the latest AI-related job postings.

Features

Automatically scrapes data from multiple platforms.

Aggregates and processes news articles for easy access.

Extracts AI-related job postings to keep users informed about the latest opportunities.

Supports scheduling for periodic updates.

Installation

To set up and run the scraper, follow these steps:

Clone this repository:
```
git clone https://github.com/tnt305/automatic-scraper.git
cd automatic-scraper
```
Install dependencies:

```pip install -r requirements.txt```

Configure API keys and credentials in the .env file (if required for authentication).

Run the scraper:

```python scraper.py```

Usage

Modify the scraper settings in config.py to adjust scraping intervals and filters.

Run the script manually or set up a cron job to automate scraping at desired intervals.

View the collected data in the output files or integrate it with a dashboard for visualization.

Contribution

Feel free to submit issues, suggestions, or pull requests to enhance the scraper's functionality.

License

This project is licensed under the MIT License.