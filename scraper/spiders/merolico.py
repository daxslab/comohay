from ads.models import Ad
from scraper.spiders.ads.merolico import MerolicoParser
from scraper.spiders.base import BaseSpider


class MerolicoSpider(BaseSpider):
    name = "merolico"
    source = 'merolico.app'
    parser = MerolicoParser(source=source)

    start_urls = [
        'https://merolico.app/category/computadoras',
        'https://merolico.app/category/compra-y-venta',
        'https://merolico.app/category/servicios',
        'https://merolico.app/category/moviles',
        'https://merolico.app/category/portatiles',
        'https://merolico.app/category/consolas',
        'https://merolico.app/category/empleos',
        'https://merolico.app/category/viviendas',
        'https://merolico.app/category/bebe',
        'https://merolico.app/category/autos',
    ]

    def parse(self, response):
        ad_page_links = response.css('.adds-wrapper > .item-list .add-title a::attr(href)').getall()
        for ad_page_link in ad_page_links:
            if not Ad.objects.filter(external_url=ad_page_link).first():
                yield response.follow(ad_page_link, self.parse_ad)

        next_page = response.css('.pagination a[rel=next]::attr(href)').get()
        if next_page is not None and self.depth > 0:
            self.depth -= 1
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(self, response):
        yield self.parser.parse_ad(response)
