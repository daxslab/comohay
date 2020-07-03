import scrapy
from categories.models import Category
from html2text import HTML2Text

from ads.models import Province, Municipality
from scraper.items import AdItem

class ProxycrawlerSpider(scrapy.Spider):
    name = "proxycrawler"

    start_urls = [
        'https://www.proxynova.com/proxy-server-list/',
    ]

    def parse(self, response):
        proxies = []
        for proxy in response.css('table#tbl_proxy_list tbody tr'):
            try:
                proxies.append({
                    'ip': proxy.css('td:nth-of-type(1) script::text').get().replace("document.write('", "").replace("');", "").strip(),
                    'port': proxy.css('td:nth-of-type(2)::text').get().strip(),
                })
            except:
                pass
        filename = 'proxies.txt'
        with open(filename, 'w') as f:
            for proxy in proxies:
                f.write(proxy['ip']+':'+proxy['port']+'\n')
