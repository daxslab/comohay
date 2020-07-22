from ads.models import Ad
from scraper.spiders.ads.bachecubano import BachecubanoParser
from scraper.spiders.base import BaseSpider


class BachecubanoSpider(BaseSpider):
    name = "bachecubano"
    source = 'bachecubano.com'
    parser = BachecubanoParser(source=source)

    start_urls = [
        'https://www.bachecubano.com/computadoras',
        'https://www.bachecubano.com/electronica',
        'https://www.bachecubano.com/servicios',
        'https://www.bachecubano.com/hogar',
        'https://www.bachecubano.com/transporte',
        'https://www.bachecubano.com/salud-y-belleza',
        'https://www.bachecubano.com/otros',
    ]

    def parse(self, response):
        ad_page_links = response.css('.product-title > a::attr(href)').getall()
        for ad_page_link in ad_page_links:
            if not Ad.objects.filter(external_url=ad_page_link).first():
                yield response.follow(ad_page_link, self.parse_ad)

        next_page = response.css('.pagination-bar a[rel=next]::attr(href)').get()
        if next_page is not None and self.depth > 0:
            self.depth -= 1
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(self, response):
        yield self.parser.parse_ad(response)