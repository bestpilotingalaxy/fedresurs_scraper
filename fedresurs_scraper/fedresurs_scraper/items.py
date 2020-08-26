# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class BankruptItem(Item):
    """Item object of bankrupt message"""
    guid = Field()
    text = Field()
    publish_date = Field()
    url = Field()
