# -*- coding: utf-8 -*-
import scrapy
import json
from sinaNews import settings, utils, urls
from sinaNews.loaders import *
from sinaNews.items import *
import os


class SinaSpider(scrapy.Spider):
    name = 'sina'

    # allowed_domains = ['feed.mix.sina.com.cn']
    def __init__(self, *args, **kwargs):
        super(SinaSpider, self).__init__(*args, **kwargs)
        self.config = kwargs.get('config')

    def start_requests(self):
        start_urls = self.config['start_urls']
        start_request_type = self.config.get('start_requests_type', 'api')  # 还可以从index页面解析
        start_callback = eval('self.parse_' + start_request_type)
        for start_url in start_urls:
            self.start_url = start_url
            perPage = int(start_url.get('max_num_per_page'))
            templateUrl = start_url.get('template_url', '')
            if start_url.get('type') == 'dynamic':
                self.classifies = {classify: True for classify in
                                   start_url.get('classifies', [0])}  # True 用来设置此分类是否继续爬取
                for classify in self.classifies.keys():
                    for pageNum in range(*start_url.get('start_end', [1, 10])):
                        if self.classifies.get(classify) == True:  # 若为False，跳过后面的页数
                            url = eval('urls.' + start_url.get('method'))(classify, perPage, pageNum, templateUrl)
                            yield scrapy.Request(url, callback=start_callback)
                        else:
                            break

            elif start_urls.get('type') == 'static':
                url = start_url.get('value')
                yield scrapy.Request(url, callback=start_callback)

    def json_parse(self, raw_string, json_formatter):
        for parser in json_formatter:
            raw_string = eval('raw_string.' + parser.get('method'))(*parser.get('args'))  # 'raw_string'和传入参数名相同
        return json.loads(raw_string)

    def get_json_needed_levels_data(self, data_types, jsonText):
        data_list = [jsonText]
        for data_type in data_types:
            jsonText = jsonText.get(data_type)
            data_list.append(jsonText)
        return data_list

    def get_common_info(self, item, data_list):
        newsInfoItem = eval(item.get('class'))()
        for key, kwargs in item.get('attrs').items():  # 得到外围共同信息
            mapField = kwargs.get('map')
            for data in data_list[:-1]:
                if key in data.keys():
                    newsInfoItem[mapField] = data.get(key)
        return newsInfoItem

    def get_single_news_info(self, item, news, newsInfoItem, response):
        loader = eval(item.get('loader'))(newsInfoItem, response=response)
        for key, kwargs in item.get('attrs').items():
            mapField = kwargs.get('map')
            if key in news.keys():
                loader.add_value(mapField, news.get(key))
        return loader.load_item()

    def parse_api(self, response):
        json_formatter = self.start_url.get('json_formatter')   #不同的网站返回的json字符串不同，格式化到只剩大括号的形式
        jsonText = self.json_parse(response.text, json_formatter)
        item = self.config.get('start_item')
        if item:
            data_types = item.get('data_types')
            data_list = self.get_json_needed_levels_data(data_types, jsonText)
            newsInfoItem = self.get_common_info(item, data_list)
            for news in data_list[-1]:  # 得到单个新闻内容信息
                newsInfoItem = self.get_single_news_info(item, news, newsInfoItem, response)
                yield newsInfoItem
                if self.classifies.get(newsInfoItem.get('classify')) == True:  # 插入数据时，如果此条数据已经存在，那么剩余链接放弃访问
                    yield scrapy.Request(newsInfoItem.get('url'), callback=self.parse_detail, dont_filter=True)
                else:
                    break

    def parse_detail(self, response):
        item = self.config.get('detail_item')
        cls = eval(item.get('class'))()
        loader = eval(item.get('loader'))(cls, response=response)
        # 动态获取属性配置
        for key, value in item.get('attrs').items():
            for extractor in value:
                if extractor.get('method') == 'xpath':
                    loader.add_xpath(key, *extractor.get('args'), **{'re': extractor.get('re')})
                if extractor.get('method') == 'css':
                    loader.add_css(key, *extractor.get('args'), **{'re': extractor.get('re')})
                if extractor.get('method') == 'value':
                    loader.add_value(key, *extractor.get('args'), **{'re': extractor.get('re')})
                if extractor.get('method') == 'attr':
                    loader.add_value(key, getattr(response, *extractor.get('args')))
        yield loader.load_item()
