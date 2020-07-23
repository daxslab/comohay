from ads.models import Ad
from scraper.spiders.ads.revolico import RevolicoParser
from scraper.spiders.base import BaseSpider


class RevolicoSpider(BaseSpider):
    name = "revolico"
    source = 'revolico.com'

    parser = RevolicoParser(source=source)

    use_proxy = True

    start_urls = [
        'https://www.revolico.com/compra-venta/',
        'https://www.revolico.com/empleos/',
        'https://www.revolico.com/autos/',
        'https://www.revolico.com/servicios/',
        'https://www.revolico.com/vivienda/',
        'https://www.revolico.com/computadoras/',
    ]

    def parse(self, response):
        ad_page_links = response.css('.container-fluid ul li[data-cy=adRow] a[href]::attr(href)').getall()
        for ad_page_link in ad_page_links:
            if not Ad.objects.filter(external_url=response.urljoin(ad_page_link)).first():
                yield response.follow(ad_page_link, self.parse_ad)

        next_page = response.css('#paginator-next::attr(href)').get()
        if next_page is not None and self.depth > 0:
            self.depth -= 1
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(self, response):
        yield self.parser.parse_ad(response)
