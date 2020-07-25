import scrapy
from scrapy.http import Request


class BaseSpider(scrapy.Spider):

    name:str
    source:str
    use_proxy:bool = False

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, errback=self.on_error)

    def on_error(self, failure):
        pass
