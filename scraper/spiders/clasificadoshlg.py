from ads.models import Ad
from scraper.spiders.ads.clasificadoshlg import ClasificadoshlgParser
from scraper.spiders.base import BaseSpider


class ClasificadoshlgSpider(BaseSpider):
    name = "clasificadoshlg"
    source = 'clasificadoshlg.com'
    parser = ClasificadoshlgParser(source=source)

    start_urls = [
        'http://clasificadoshlg.com/articulos-en-venta',
        'http://clasificadoshlg.com/cursos',
        'http://clasificadoshlg.com/ofertas-de-empleo',
        'http://clasificadoshlg.com/servicios',
        'http://clasificadoshlg.com/vehiculos',
        'http://clasificadoshlg.com/comunidad',
        'http://clasificadoshlg.com/todo-lo-demas_1',
    ]

    def parse(self, response):
        ad_page_links = response.css('.listing-card > a.title::attr(href)').getall()
        for ad_page_link in ad_page_links:
            if not Ad.objects.filter(external_url=ad_page_link).first():
                yield response.follow(ad_page_link, self.parse_ad)

        next_page = response.css('.paginate a.searchPaginationNext::attr(href)').get()
        if next_page is not None and self.depth > 0:
            self.depth -= 1
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(self, response):
        yield self.parser.parse_ad(response)