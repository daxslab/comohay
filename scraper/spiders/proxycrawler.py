import scrapy

class ProxycrawlerSpider(scrapy.Spider):
    name = "proxycrawler"

    start_urls = [
        'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
    ]

    def parse(self, response):
        filename = 'proxies.txt'
        with open(filename, 'w') as f:
            f.write(str(response.text))
