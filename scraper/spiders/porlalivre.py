from ads.models import Ad
from scraper.spiders.ads.porlalivre import PROVINCE_MAPPING, PorlalivreParser
from scraper.spiders.base import BaseSpider


class PorlalivreSpider(BaseSpider):
    name = "porlalivre"
    source = 'porlalivre.com'

    parser = PorlalivreParser(source=source)

    base_url = 'https://porlalivre.com'

    base_pages = [
        '/viviendas/',
        # '/celulares/',
        # '/autos/',
        # '/portatiles/',
        # '/comunidad/',
        # '/se-vende/',
        # '/computadoras/',
        # '/consolas-juegos/',
        # '/servicios/',
    ]

    start_urls = []

    for base_page in base_pages:
        for province in PROVINCE_MAPPING:
            start_urls.append(base_url[:8] + province + '.' + base_url[8:] + base_page)

    def parse(self, response):
        ad_page_links = response.css('a.classified-link::attr(href)').getall()
        for ad_page_link in ad_page_links:
            try:
                if not Ad.objects.filter(external_source=self.source, external_id=ad_page_link.split('-')[-1].strip('/')).first():
                    yield response.follow(ad_page_link, self.parse_ad)

            except Exception as error:
                self.logger.error(str(error))

        next_page = response.css('.pagination li:last-of-type a::attr(href)').get()
        if next_page is not None and self.depth > 0:
            self.depth -= 1
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(self, response):
        yield self.parser.parse_ad(response)