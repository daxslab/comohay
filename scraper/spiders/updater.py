from datetime import timedelta
from importlib import import_module

from django.utils import timezone
from scrapy import Request

from ads.models import Ad
from comohay import settings
from scraper.spiders.base import BaseSpider


class UpdaterSpider(BaseSpider):
    name = "updater"

    use_proxy = True

    def start_requests(self):
        ads_query_set = Ad.objects.filter(
            updated_at__lt=timezone.now()-timedelta(days=settings.AD_UPDATE_PERIOD)
        ).exclude(
            external_url__isnull=True,
            external_url=''
        )
        for ad in ads_query_set:
            meta = {
                'external_source':ad.external_source
            }
            if ad.external_source != 'revolico.com':
                meta['proxy'] = None
            yield Request(ad.external_url,
                          dont_filter=True,
                          errback=self.on_error,
                          meta=meta
                          )


    def parse(self, response):
        external_source = response.meta['external_source']
        parser_name = None
        parser_class = None
        for name, source in settings.EXTERNAL_SOURCES.items():
            if source == external_source:
                parser_name = name
        try:
            parser_module = import_module('scraper.spiders.ads.%s' % parser_name)
            parser_class = getattr(parser_module, parser_name.capitalize()+'Parser')
        except Exception as e:
            self.logger.error(str(e))
        if parser_class:
            yield parser_class(source=external_source).parse_ad(response)

    def on_error(self, failure):
        if failure.value.response.status == 404:
            Ad.objects.filter(external_url=failure.request.url).delete()

