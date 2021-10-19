import json
from typing import Union

from django.db.models import QuerySet, Q, Subquery
from comohay import settings
from currencies.models import CurrencyAd
from scraper.items import AdItem
from scraper.utils import get_spider_name_by_source
from ads.models import Ad
from scrapy import Request
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings


def get_update_request(ad: Ad, error_callback=None) -> Request:

    if ad.external_source.startswith('t.me/'):
        source_name = settings.TELEGRAM_SOURCE_NAME
    else:
        source_name = get_spider_name_by_source(ad.external_source)

    meta = {
        'source_name': source_name,
        'ad_id': ad.id
    }

    no_proxy = True

    if source_name != settings.TELEGRAM_SOURCE_NAME:
        spider_loader = SpiderLoader(get_project_settings())
        spider = spider_loader.load(source_name)
        no_proxy = not getattr(spider, 'use_proxy', False)

    if no_proxy:
        meta['proxy'] = None  # disabling proxy

    # FIXME: revolico graphql api corner case, fix spider architecture
    if source_name == 'revolico':

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

        return Request(
            url,
            method='POST',
            dont_filter=True,
            errback=error_callback,
            body=json.dumps(query),
            headers={'Content-Type': 'application/json'},
            meta=meta
        )
    else:
        return Request(
            ad.external_url,
            dont_filter=True,
            errback=error_callback,
            meta=meta
        )


CURRENCYADS = 'currencyads'
NON_CURRENCYADS = 'non-currencyads'
ALL = 'all'


def get_ads_to_update_queryset(update_type: str, sources: list) -> QuerySet:
    query = Q(is_deleted=False)

    if sources:
        external_sources = []

        for source in sources:
            if source in settings.EXTERNAL_SOURCES:
                external_sources.append(settings.EXTERNAL_SOURCES[source])
            elif source == settings.TELEGRAM_SOURCE_NAME:
                external_sources.append('t.me/')

        if external_sources:
            external_sources_query = Q()
            for external_source in external_sources:
                external_sources_query |= Q(external_source__startswith=external_source)

            query = query & external_sources_query

    ads_queryset = Ad.objects.filter(query)

    currencyads_ids_queryset = CurrencyAd.objects.filter(ad__is_deleted=False).values('ad__id')

    if update_type == NON_CURRENCYADS:
        ads_queryset = ads_queryset.exclude(id__in=Subquery(currencyads_ids_queryset))
    elif update_type == CURRENCYADS:
        ads_queryset = ads_queryset.filter(id__in=Subquery(currencyads_ids_queryset))

    ads_queryset.exclude(Q(external_url__isnull=True) | Q(external_url=''))
    return ads_queryset


# OJO: tremenda locura aquí, pensar bien antes de hacer cambios
def parse_updater_response(response) -> Union[AdItem, None]:
    source_name = response.meta['source_name']
    ad_id = response.meta['ad_id']

    # TODO: create custom request using the hogarencuba api and create a parse to update the incoming ads.
    if source_name == "hogarencuba":
        return None

    # TODO: add a telegram parser
    # Here we only remove the ad when no longer exists, we don't update it
    if source_name == settings.TELEGRAM_SOURCE_NAME:
        widget = response.css('#widget').get(default=None)
        # if there is no widget then assume the telegram message was removed
        if widget is None:
            Ad.objects.get(id=ad_id).delete()

        return None

    # FIXME: revolico graphql api corner case, fix spider architecture
    if source_name == "revolico":
        response_object = json.loads(response.body)[0]
        response = response_object['data']['ad']

    spider_loader = SpiderLoader(get_project_settings())
    spider = spider_loader.load(source_name)

    if spider.parser.is_not_found(response):
        Ad.objects.get(id=ad_id).delete()
        return None

    return spider.parser.parse_ad(response)
