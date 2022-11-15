# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class SpiderAppsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class EbayCategoryItem(scrapy.Item):
    url = scrapy.Field()
    kws = scrapy.Field()


class EbayUserInfoItem(scrapy.Item):
    username = scrapy.Field()
    user_link = scrapy.Field()
    is_store = scrapy.Field()
    store_name = scrapy.Field()
    stars_num = scrapy.Field()
    user_location = scrapy.Field()
    listing_num = scrapy.Field()
    listing_category = scrapy.Field()
