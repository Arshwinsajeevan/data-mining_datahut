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

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers=self.custom_headers)

    def parse(self, response):
        if not getattr(self, "_logged_headers", False):
            try:
                hdrs = {
                    k.decode() if isinstance(k, bytes) else k:
                    v.decode() if isinstance(v, bytes) else v
                    for k, v in response.request.headers.items()
                }
            except Exception:
                hdrs = dict(response.request.headers)
            self.logger.info("REQUEST HEADERS SENT: %s", hdrs)
            self._logged_headers = True

        if response.status == 403:
            self.logger.error("GOT 403 for %s", response.url)
            self.logger.error("403 RESPONSE SNIPPET: %s", (response.text or "")[:1200])
            return

        for href in response.xpath("//a[contains(@href,'/agents/')]/@href").getall():
            full = response.urljoin(href)
            if full not in self.visited_profiles:
                self.visited_profiles.add(full)
                yield response.follow(full, self.parse_agent, headers=self.custom_headers)

        next_page = response.xpath("//a[@aria-label='Next']/@href").get()
        if next_page:
            yield response.follow(next_page, self.parse, headers=self.custom_headers)

    def parse_agent(self, response):
        item = EwmAgentItem()
        item["profile_url"] = response.url

        #Name split
        full_name = response.xpath(
            "normalize-space(//strong[contains(text(),'Name')]/following-sibling::span/text())"
        ).get() or ""
        parts = [p.strip() for p in full_name.split() if p.strip()]
        item["first_name"] = parts[0] if parts else ""
        item["middle_name"] = " ".join(parts[1:-1]) if len(parts) > 2 else ""
        item["last_name"] = parts[-1] if len(parts) >= 2 else ""
        
        #Address split
        street = response.xpath(
            "//th[contains(text(),'Address')]/following-sibling::td/text()[1]"
        ).get()
        line2 = response.xpath(
            "//th[contains(text(),'Address')]/following-sibling::td/text()[2]"
        ).get()
        item["address"] = street.strip() if street else ""
        if line2:
            line2 = line2.strip()
            if "," in line2:
                city_part, rest = line2.split(",", 1)
                item["city"] = city_part.strip()
                rest = rest.strip().split()
                item["state"] = rest[0] if rest else ""
                item["zipcode"] = rest[-1] if rest else ""
            else:
                item["city"], item["state"], item["zipcode"] = line2, "", ""
        else:
            item["city"], item["state"], item["zipcode"] = "", "", ""
            
        #Image url
        style = response.xpath("//div[contains(@class,'listing-user-image')]//a/@style").get() or ""
        m = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
        image_url = m.group(1) if m else response.xpath("//img[contains(@src,'profiles')]/@src").get() or ""
        item["image_url"] = response.urljoin(image_url) if image_url else ""
        
        #Title, websites
        h1 = response.xpath("normalize-space(//div[contains(@class,'content-title-inner')]//h1/text())").get() or ""
        item["title"] = h1.split(" - ", 1)[1].strip() if " - " in h1 else ""

        website = response.xpath("//a[contains(normalize-space(.),'Visit My Website')]/@href").get()
        item["website"] = response.urljoin(website) if website else ""

        #Phones
        office = response.xpath("//strong[normalize-space()='Office']/following-sibling::span//a/text()").getall()
        item["office_phone_numbers"] = [x.strip() for x in office if x and x.strip()]
        direct = response.xpath("//strong[normalize-space()='Direct Line']/following-sibling::span//a/text()").get()
        if direct:
            item["agent_phone_numbers"] = [direct.strip()]
        else:
            cell = response.xpath("//strong[normalize-space()='Cell']/following-sibling::span//a/text()").get()
            item["agent_phone_numbers"] = [cell.strip()] if cell else []

        #Social links
        social_links = response.xpath("//div[contains(@class,'listing-user-social')]//a/@href").getall()
        social = {}
        for s in social_links:
            s = s.strip()
            if "facebook.com" in s and "facebook" not in social:
                social["facebook"] = s
            elif "twitter.com" in s and "twitter" not in social:
                social["twitter"] = s
            elif "linkedin.com" in s and "linkedin" not in social:
                social["linkedin"] = s
            elif "instagram.com" in s and "instagram" not in social:
                social["instagram"] = s
            elif "youtube.com" in s and "youtube" not in social:
                social["youtube"] = s
        item["social"] = social

        #Languages and description
        langs = response.xpath("//strong[contains(text(),'Languages')]/following-sibling::span/text()").get()
        item["languages"] = [l.strip() for l in langs.split(",") if l.strip()] if langs else []
        desc_nodes = response.xpath("//h2[starts-with(normalize-space(.),'About')]/following-sibling::p//text()").getall()
        item["description"] = " ".join([t.strip() for t in desc_nodes if t and t.strip()])

        yield item
