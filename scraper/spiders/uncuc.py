from ads.models import Ad
from scraper.spiders.ads.uncuc import UncucParser
from scraper.spiders.base import BaseSpider


class UncucSpider(BaseSpider):
    name = "uncuc"
    source = '1cuc.com'
    parser = UncucParser(source=source)

    start_urls = [
        'https://1cuc.com/cuba/search/bienes-raices-casas/',
        'https://1cuc.com/cuba/search/electronica-equipo-de-cocina/',
        'https://1cuc.com/cuba/search/ropa-zapatos-accesorios/',
        'https://1cuc.com/cuba/search/belleza-salud-cosmetico/',
        'https://1cuc.com/cuba/search/transporte/',
        'https://1cuc.com/cuba/search/muebles-hogar-jardin-otros/',
        'https://1cuc.com/cuba/search/servicios/',
        'https://1cuc.com/cuba/search/trabajo-empleo/',
        'https://1cuc.com/cuba/search/construccion-reparacion/',
        'https://1cuc.com/cuba/search/deportes-ocio/',
        'https://1cuc.com/cuba/search/mascotas-animales/',
        'https://1cuc.com/cuba/search/productos-bebes-ninos/',
        'https://1cuc.com/cuba/search/aficion-musica-arte/',
        'https://1cuc.com/cuba/search/cursos-educacion/',
        'https://1cuc.com/cuba/search/alimentos-comida-bebidas/',
        'https://1cuc.com/cuba/search/sin-fines-lucro/',
    ]

    def parse(self, response):
        ad_page_links = response.css('div.j-list-desktop .sr-page__list__item h3 > a::attr(href)').getall()
        for ad_page_link in ad_page_links:
            if not Ad.objects.filter(external_url=ad_page_link).first():
                yield response.follow(ad_page_link, self.parse_ad)

        next_page = response.css('ul.pager a.j-pgn-page::attr(href)').get()
        if next_page is not None and self.depth > 0:
            self.depth -= 1
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(self, response):
        yield self.parser.parse_ad(response)