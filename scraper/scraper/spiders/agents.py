import scrapy
import re
from ..items import AgentItem

class AgentsSpider(scrapy.Spider):
    name = "agents"
    allowed_domains = ["ewm.com"]
    start_urls = ["https://www.ewm.com/agents.php"]
    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0',
        'Referer': 'https://www.google.com/',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    custom_settings = {
    }

    def parse(self, response):
        """Parse listing page: collect profile links and pagination"""
        profile_links = response.xpath("//a[contains(@href,'/agents/') and descendant::img]/@href").getall()

        if not profile_links:
            profile_links = response.xpath("//a[contains(@href,'/agents/')]/@href").getall()

        for href in profile_links:
            yield response.follow(href, callback=self.parse_agent, headers=self.custom_headers)

        # Pagination
        next_page = response.xpath("//a[contains(@class,'next') or contains(text(),'>') or contains(text(),'Next')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse, headers=self.custom_headers)
        else:
            next_page = response.xpath("//link[@rel='next']/@href").get()
            if next_page:
                yield response.follow(next_page, callback=self.parse, headers=self.custom_headers)

    def parse_agent(self, response):
        """Parse agent detail page and populate AgentItem"""
        item = AgentItem()
        item['profile_url'] = response.url

        # NAME
        full_name = response.xpath("//h1/text()").get()
        if not full_name:
            full_name = response.xpath("//div[contains(@class,'agent-name')]/text()").get()
        full_name = (full_name or "").strip()

        # first, middle, last 
        name_parts = [p.strip() for p in full_name.split() if p.strip()]
        if len(name_parts) == 0:
            item['first_name'] = item['middle_name'] = item['last_name'] = ""
        elif len(name_parts) == 1:
            item['first_name'] = name_parts[0]
            item['middle_name'] = ""
            item['last_name'] = ""
        elif len(name_parts) == 2:
            item['first_name'] = name_parts[0]
            item['middle_name'] = ""
            item['last_name'] = name_parts[1]
        else:
            item['first_name'] = name_parts[0]
            item['last_name'] = name_parts[-1]
            item['middle_name'] = " ".join(name_parts[1:-1])

        # TITLE
        title = response.xpath("//h1/following-sibling::*[1]//text()").get()
        if not title:
            title = response.xpath("//div[contains(@class,'title')]/text()").get()
        item['title'] = (title or "").strip()

        # IMAGE
        image = response.xpath("//img[contains(@class,'profile') or contains(@class,'agent')]/@src").get()
        if not image:
            image = response.xpath("//div[contains(@class,'agent-image')]//img/@src").get()
        item['image_url'] = image or ""

        # CONTACT 
        address = response.xpath("//div[contains(@class,'contact-information')]//li[contains(.,'Address')]/text()").get()
        if not address:
            address_parts = response.xpath("//div[contains(@class,'contact-information')]//text()").getall()
            address = " ".join([a.strip() for a in address_parts if a.strip()])[:2000] if address_parts else ""
        item['address'] = (address or "").strip()

        # Extracting city/state/zip 
        city_state_zip = response.xpath("//div[contains(@class,'contact-information')]//span[contains(@class,'city')]/text()").get()
        if not city_state_zip:
            city_state_zip = ""
            addr_text = item['address']
            m = re.search(r"([A-Za-z\s]+),\s*([A-Z]{2})\s*(\d{5})", addr_text)
            if m:
                item['city'] = m.group(1).strip()
                item['state'] = m.group(2).strip()
                item['zipcode'] = m.group(3).strip()
            else:
                m = re.search(r"([A-Za-z\s]+),\s*([A-Z]{2})", addr_text)
                if m:
                    item['city'] = m.group(1).strip()
                    item['state'] = m.group(2).strip()
                    item['zipcode'] = ""
                else:
                    item['city'] = item['state'] = item['zipcode'] = ""
        else:
            parts = re.split(r',|\s{2,}', city_state_zip)
            if len(parts) >= 1:
                item['city'] = parts[0].strip()
            if len(parts) >= 2:
                s = parts[1].strip()
                m = re.match(r"([A-Z]{2})\s*(\d{5})?", s)
                if m:
                    item['state'] = m.group(1)
                    item['zipcode'] = m.group(2) or ""
                else:
                    item['state'] = s
                    item['zipcode'] = ""

        # PHONE numbers
        def extract_phone(xpath_expr):
            text = response.xpath(xpath_expr).get()
            if text:
                return text.strip()
            return ""

        office_phone = response.xpath("//li[contains(translate(.,'OFFICE','office'),'Office')]/text()").get()
        office_phone = office_phone or response.xpath("//li[contains(.,'Office')]/text()").get()
        direct_phone = response.xpath("//li[contains(.,'Direct')]/text()").get()
        cell_phone = response.xpath("//li[contains(.,'Cell')]/text()").get()

        if not any([office_phone, direct_phone, cell_phone]):
            tel_links = response.xpath("//a[starts-with(@href,'tel:')]/@href").getall()
            tel_links = [t.replace("tel:", "").strip() for t in tel_links]
            item['office_phone_numbers'] = tel_links[:1] if tel_links else []
            item['agent_phone_numbers'] = tel_links[1:2] if len(tel_links) > 1 else []
        else:
            item['office_phone_numbers'] = [office_phone] if office_phone else []
            agent_nums = []
            if cell_phone:
                agent_nums.append(cell_phone)
            if direct_phone:
                agent_nums.append(direct_phone)
            item['agent_phone_numbers'] = agent_nums

        # Website 
        website = response.xpath("//a[contains(.,'Visit My Website')]/@href").get()
        if not website:
            website = response.xpath("//a[contains(.,'Website') or contains(.,'Personal Site')]/@href").get()
        item['website'] = website or ""

        # Social links
        item['social'] = {
            'facebook_url': response.xpath("//a[contains(@href,'facebook.com')]/@href").get() or "",
            'twitter_url': response.xpath("//a[contains(@href,'twitter.com')]/@href").get() or "",
            'linkedin_url': response.xpath("//a[contains(@href,'linkedin.com')]/@href").get() or ""
        }

        # Languages 
        langs = response.xpath("//*[contains(translate(text(),'LANGUAGES','languages'),'Languages')]/following-sibling::*[1]//text()").getall()
        if not langs:
            text = response.xpath("//*[contains(text(),'Languages')]/text()").get()
            if text and ":" in text:
                langs = [l.strip() for l in text.split(":",1)[1].split(",") if l.strip()]
        item['languages'] = [l.strip() for l in langs if l.strip()] if langs else []

        # Description 
        desc_parts = response.xpath("//div[contains(@class,'about') or contains(@class,'description') or contains(@id,'bio')]//text()").getall()
        if not desc_parts:
            desc_parts = response.xpath("//div[contains(@class,'agent-bio')]//text()").getall()
        item['description'] = " ".join([d.strip() for d in desc_parts if d.strip()])

        # Final defaults
        for key in ['address','city','state','zipcode','image_url','title','website','languages','description','office_phone_numbers','agent_phone_numbers','social']:
            if key not in item:
                item[key] = "" if key in ['address','city','state','zipcode','image_url','title','website','description'] else []

        yield item
