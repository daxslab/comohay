import json
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
        for ad in ads_query_set.iterator():
            spider_name = get_spider_name_by_source(ad.external_source)
            spider = self.spider_loader.load(spider_name)
            meta = {
                'spider': spider,
                'ad_id': ad.id
            }
            if not getattr(spider, 'use_proxy', False):
                meta['proxy'] = None

            # FIXME: revolico graphql api corner case, fix spider architecture
            if spider_name == 'revolico':
                query = [
                    {
                        'operationName': 'AdDetails',
                        "variables": {
                            "id": ad.external_id
                        },
                        'query': "query AdDetails($id: Int!, $token: String) { ad(id: $id, token: $token) { ...Ad subcategory { id title slug parentCategory { id title slug __typename } __typename } viewCount permalink __typename } } fragment Ad on AdType {id title price currency shortDescription description email phone permalink imagesCount updatedOnToOrder updatedOnByUser isAuto province {id name slug __typename} municipality {id name slug __typename } subcategory {id title __typename} __typename }"
                    }
                ]
                url = 'https://api.revolico.app/graphql/'
                meta['query'] = query
                yield Request(url, method='POST', dont_filter=True, errback=self.on_error,
                              body=json.dumps(query),
                              headers={'Content-Type': 'application/json'},
                              meta=meta
                              )
            else:

                yield Request(ad.external_url,
                              dont_filter=True,
                              errback=self.on_error,
                              meta=meta
                              )

    def parse(self, response):
        spider = response.meta['spider']
        ad_id = response.meta['ad_id']

        # FIXME: revolico graphql api corner case, fix spider architecture
        if spider.name == "revolico":
            response_object = json.loads(response.body)[0]
            response = response_object['data']['ad']

        if spider.parser.is_not_found(response):
            Ad.objects.get(id=ad_id).delete()
        else:
            yield spider.parser.parse_ad(response)

    def on_error(self, failure):
        if failure.value.response.status == 404:
            Ad.objects.filter(external_url=failure.request.url).delete()
