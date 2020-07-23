from datetime import timedelta

from django.utils import timezone
from scrapy import Request
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings

from ads.models import Ad
from comohay import settings
from scraper.spiders.base import BaseSpider
from scraper.utils import get_spider_name_by_source


class UpdaterSpider(BaseSpider):
    name = "updater"

    use_proxy = True

    spider_loader = SpiderLoader(get_project_settings())

    def start_requests(self):

        ads_query_set = Ad.objects.filter(
            updated_at__lt=timezone.now()-timedelta(days=settings.AD_UPDATE_PERIOD)
        ).exclude(
            external_url__isnull=True,
            external_url=''
        )
        for ad in ads_query_set:
            spider_name = get_spider_name_by_source(ad.external_source)
            spider = self.spider_loader.load(spider_name)
            meta = {
                'spider': spider
            }
            if not getattr(spider, 'use_proxy', False):
                meta['proxy'] = None
            yield Request(ad.external_url,
                          dont_filter=True,
                          errback=self.on_error,
                          meta=meta
                          )


    def parse(self, response):
        spider = response.meta['spider']
        yield spider.parser.parse_ad(response)

    def on_error(self, failure):
        if failure.value.response.status == 404:
            Ad.objects.filter(external_url=failure.request.url).delete()
