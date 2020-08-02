from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
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

    source:str

    update_period:int

    def start_requests(self):

        query = Q(updated_at__lt=timezone.now()-timedelta(days=self.update_period))

        if self.source:
            external_sources = []
            for source in self.source:
                if source in settings.EXTERNAL_SOURCES:
                    external_sources.append(settings.EXTERNAL_SOURCES[source])
            if external_sources:
                query = query & Q(external_source__in=external_sources)


        ads_query_set = Ad.objects.filter(query)

        ads_query_set.exclude(
            Q(external_url__isnull=True) | Q(external_url='')
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
        if spider.parser.is_not_found(response):
            Ad.objects.filter(external_url=response.request.url).delete()
        else:
            yield spider.parser.parse_ad(response)

    def on_error(self, failure):
        if failure.value.response.status == 404:
            Ad.objects.filter(external_url=failure.request.url).delete()