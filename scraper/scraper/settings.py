"""Project settings for the EWM Scrapy spider."""

# Basic Scrapy project config
BOT_NAME = "scraper"
SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

# Robots.txt compliance
ROBOTSTXT_OBEY = False

# Close spider after this many items
CLOSESPIDER_ITEMCOUNT = 1000

# Feed exports (JSON + CSV)
FEEDS = {
    "output/ewm_agents.json": {"format": "json", "encoding": "utf8", "indent": 2},
    "output/ewm_agents.csv": {"format": "csv", "encoding": "utf8"},
}

# Concurrency & politeness
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4
DOWNLOAD_DELAY = 0.5
RANDOMIZE_DOWNLOAD_DELAY = True

# Timeouts & retry rules
DOWNLOAD_TIMEOUT = 20
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [429, 403, 500, 502, 503, 504, 522, 524]

# AutoThrottle 
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Cookies 
COOKIES_ENABLED = True

# Default realistic request headers
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:145.0) "
        "Gecko/20100101 Firefox/145.0"
    ),
    "Referer": "https://www.google.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}

# Pipelines
ITEM_PIPELINES = {
    "scraper.pipelines.SQLiteStorePipeline": 300,
}

# Job resume directory 
# JOBDIR = "crawls/ewm-1"

# Logging and feed encoding
LOG_LEVEL = "INFO"
FEED_EXPORT_ENCODING = "utf-8"
