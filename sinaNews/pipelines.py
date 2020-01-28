# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.exceptions import DropItem
import os
import time



class SinanewsPipeline(object):

    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('HOST'),
            database=crawler.settings.get('DATABASE'),
            user=crawler.settings.get('USER'),
            password=crawler.settings.get('PASSWORD'),
            port=crawler.settings.get('PORT')
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        data = dict(item)
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))
        sql = 'insert into {table_name}({keys}) values ({values})'.format(
            table_name=item.__class__.__name__, keys=keys, values=values)
        try:
            self.cursor.execute(sql, tuple(data.values()))
        except Exception as e:
            if '1062' in str(e): #不可空字段为空
                spider.classifies[data.get('classify')] = False
            else:   #其他情况保存错误以及url
                with open(str(spider.name) + "_error_and_url.txt", "a") as f:
                    f.write(str(e)+':'+data.get('url','no_url') + "\n")
            raise DropItem
        finally:
            self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()

