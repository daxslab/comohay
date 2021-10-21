import json
import scraper
from ads.models import Ad
import scraper.services.updater_service
from scraper.spiders.base import BaseSpider


class UpdaterSpider(BaseSpider):
    name = "updater"

    use_proxy = True

    sources: list

    update_type: str = 'all'

    def start_requests(self):

        ads_queryset = scraper.services.updater_service.get_ads_to_update_queryset(
            update_type=self.update_type,
            sources=self.sources
        )

        for ad in ads_queryset.iterator():
            request = scraper.services.updater_service.get_update_request(ad, error_callback=self.on_error)
            yield request

    def parse(self, response):
        ad_item = scraper.services.updater_service.parse_updater_response(response)
        if ad_item:
            yield ad_item

    def on_error(self, failure):
        if failure.value.response.status == 404:
            Ad.objects.filter(external_url=failure.request.url).first().delete(soft=True)
