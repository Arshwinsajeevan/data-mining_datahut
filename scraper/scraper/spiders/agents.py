# scraper/scraper/spiders/agents.py
import re
import scrapy
from ..items import EwmAgentItem


class AgentsSpider(scrapy.Spider):
    name = "agents"
    allowed_domains = ["ewm.com"]
    start_urls = ["https://www.ewm.com/agents.php"]

    handle_httpstatus_list = [403]
    visited_profiles = set()

    custom_headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:145.0) "
            "Gecko/20100101 Firefox/145.0"
        ),
        "Referer": "https://www.google.com/",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }