from ads.models import Ad
from scraper.spiders.ads.timbirichi import TimbirichiParser
from scraper.spiders.base import BaseSpider


class TimbirichiSpider(BaseSpider):
    name = "timbirichi"
    source = 'timbirichi.com'
    parser = TimbirichiParser(source=source)

    start_urls = [
        'https://www.timbirichi.com/computadoras',
        'https://www.timbirichi.com/compra-y-venta',
        'https://www.timbirichi.com/moviles-y-tabletas',
        'https://www.timbirichi.com/servicios',
        'https://www.timbirichi.com/viviendas',
        'https://www.timbirichi.com/vehiculos-y-piezas',
        'https://www.timbirichi.com/electrodomesticos',
        'https://www.timbirichi.com/empleos',
        'https://www.timbirichi.com/amor-amistad',
        'https://www.timbirichi.com/comunidad',
        'https://www.timbirichi.com/juguetes-de-adultos',
    ]

    def parse(self, response):
        ad_page_links = response.css('.contenedor-de-anuncios > a.anuncio-list::attr(href)').getall()
        for ad_page_link in ad_page_links:
            if not Ad.objects.filter(external_url=ad_page_link).first():
                yield response.follow(ad_page_link, self.parse_ad)

        next_page = response.css('.pagination a[rel=next]::attr(href)').get()
        if next_page is not None and self.depth > 0:
            self.depth -= 1
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(self, response):
        yield self.parser.parse_ad(response)