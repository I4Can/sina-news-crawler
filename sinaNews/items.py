# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.org/en/latest/topics/items.html

from scrapy import Field, Item


# Item类名必须和数据库中表名一致
class newsText(Item):
    url = Field()
    text = Field()


class SinaText(newsText):
    pass


class SinaNewsInfos(Item):
    # define the fields for your item here like:
    classify = Field()  # 对应lid
    title = Field()
    time = Field()
    url = Field()
    wapurl = Field()
    intro = Field()
    media_name = Field()
    keywords = Field()


class SohuNewsInfos(Item):
    # define the fields for your item here like:
    classify = Field()
    authorId = Field()  # 类别
    authorName = Field()  # 出版社
    title = Field()
    time = Field()  # publicTime
    url = Field()
    media_name = Field()
    keywords = Field()  # tags


class XinhuaNewsInfos(Item):
    # define the fields for your item here like:
    classify = Field()  # NodeId
    title = Field()
    intro = Field()  # abstract
    time = Field()  # pubTime
    url = Field()  # LinkUrl
    media_name = Field()
    keywords = Field()  # keyword
    author = Field()
    editor = Field()


class XinhuaText(newsText):
    pass
