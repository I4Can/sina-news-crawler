from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Join, Compose
import re
import datetime


class SinaNewsInfoLoader(ItemLoader):
    default_output_processor = TakeFirst()
    time_out = Compose(Join(), lambda time: datetime.datetime.fromtimestamp(int(time)))


class SinaTextLoader(ItemLoader):
    text_out = Compose(Join(),  #去除不可识别字符串
                       lambda text: re.sub(r'\u3000', '', text),
                       lambda text: re.sub(r'\s*\n\s*', '\n', text),
                       lambda text: re.sub(r'[ \xa0?]+', ' ', text),
                       # lambda text: re.sub(r'\s*\n\s*', r'\1', text),
                       )


class XinhuaNewsInfoLoader(ItemLoader):
    default_output_processor = TakeFirst()
    time_out = Compose(Join(), lambda time: datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))


class XinhuaTextLoader(ItemLoader):
    text_out = Compose(Join(),
                       lambda text: re.sub(r'\u3000', '', text),
                       lambda text: re.sub(r'\s*\n\s*', '\n', text),
                       lambda text: re.sub(r'[ \xa0?]+', ' ', text),
                       )
