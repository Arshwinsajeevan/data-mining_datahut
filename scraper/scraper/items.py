"""Data structure for EWM agent items."""

import scrapy

class EwmAgentItem(scrapy.Item):
    profile_url = scrapy.Field()
    first_name = scrapy.Field()
    middle_name = scrapy.Field()
    last_name = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    zipcode = scrapy.Field()
    image_url = scrapy.Field()
    title = scrapy.Field()
    website = scrapy.Field()
    office_phone_numbers = scrapy.Field()
    agent_phone_numbers = scrapy.Field()
    social = scrapy.Field()
    languages = scrapy.Field()
    description = scrapy.Field()
