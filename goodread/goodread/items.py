# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GoodreadItem(scrapy.Item):
    bookUrl = scrapy.Field()
    number = scrapy.Field()
    bookname = scrapy.Field()
    author = scrapy.Field()
    prices = scrapy.Field()
    describe = scrapy.Field()
    rating = scrapy.Field()
    ratingcount = scrapy.Field()
    reviews = scrapy.Field()
    fivestars = scrapy.Field()
    fourstars = scrapy.Field()
    threestars = scrapy.Field()
    twostars = scrapy.Field()
    onestar = scrapy.Field()
    pages = scrapy.Field()
    publish = scrapy.Field()
    authorUrl = scrapy.Field()
    genre = scrapy.Field()
    score = scrapy.Field()
    votes = scrapy.Field()

