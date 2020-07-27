from ads.models import Ad
from scrapy import Selector
from scraper.spiders.ads.porlalivre import PROVINCE_MAPPING, PorlalivreParser
from scraper.spiders.base import BaseSpider


class PorlalivreSpider(BaseSpider):
    name = "porlalivre"
    source = 'porlalivre.com'

    parser = PorlalivreParser(source=source)

    base_url = 'https://porlalivre.com'

    base_pages = [
        '/viviendas/',
        '/celulares/',
        '/autos/',
        '/portatiles/',
        '/comunidad/',
        '/se-vende/',
        '/computadoras/',
        '/consolas-juegos/',
        '/servicios/',
    ]

    start_urls = []

    for base_page in base_pages:
        for province in PROVINCE_MAPPING:
            start_urls.append(base_url[:8] + province + '.' + base_url[8:] + base_page)

    def parse(self, response):
        ads = response.css('div.classified-wrapper').getall()
        for ad in ads:
            link = Selector(text=ad).css('a.classified-link::attr(href)').get()
            date_text = Selector(text=ad).css('.media-body > ul.list-inline li:nth-of-type(1)::text').get()
            try:
                if not Ad.objects.filter(external_source=self.source, external_id=link.split('-')[-1].strip('/')).first():
                    yield response.follow(link, self.parse_ad, meta=dict(ad_date=date_text))

            except Exception as error:
                self.logger.error(str(error))

        next_page = response.css('.pagination li:last-of-type a::attr(href)').get()
        if next_page is not None and self.depth > 0:
            self.depth -= 1
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(self, response):
        yield self.parser.parse_ad(response)