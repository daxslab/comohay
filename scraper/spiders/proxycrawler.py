import scrapy

class ProxycrawlerSpider(scrapy.Spider):
    name = "proxycrawler"

    start_urls = [
        'https://www.freeproxy.world/?type=http&anonymity=&country=&speed=500&port=&page=1',
        # 'https://www.freeproxy.world/?type=http&anonymity=&country=&speed=500&port=&page=2',
    ]

    def parse(self, response):
        proxies = []
        for proxy in response.css('.proxy-table table.layui-table tbody tr'):
            try:
                proxies.append({
                    'ip': proxy.css('td:nth-of-type(1)::text').get().strip(),
                    'port': proxy.css('td:nth-of-type(2) > a::text').get().strip(),
                })
            except:
                pass
        filename = 'proxies.txt'
        with open(filename, 'w') as f:
            for proxy in proxies:
                f.write(proxy['ip']+':'+proxy['port']+'\n')
