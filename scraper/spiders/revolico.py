import json
from copy import deepcopy

from scrapy import Request

from scraper.spiders.ads.revolico import RevolicoParser
from scraper.spiders.base import BaseSpider


class RevolicoSpider(BaseSpider):
    name = "revolico"
    source = 'revolico.com'

    parser = RevolicoParser(source=source)

    use_proxy = True

    query = [
        {
            'operationName': 'AdsList',
            'query': 'query AdsList($category: ID, $subcategory: ID, $sort: [adsPerPageSort], $categorySlug: String, $subcategorySlug: String, $page: Int, $pageLength: Int) {adsPerPage(category: $category, subcategory: $subcategory, sort: $sort, categorySlug: $categorySlug, subcategorySlug: $subcategorySlug, page: $page, pageLength: $pageLength) {pageInfo {...PaginatorPageInfo __typename} edges {node {id title price currency shortDescription description email phone permalink imagesCount updatedOnToOrder updatedOnByUser isAuto province {id name slug __typename} municipality {id name slug __typename } subcategory {id title __typename} __typename } __typename } meta { total __typename } __typename }} fragment PaginatorPageInfo on CustomPageInfo { startCursor endCursor hasNextPage hasPreviousPage pageCount __typename}',
            'variables': {
                'categorySlug': 'empleos',
                'page': 1,
                'pageLength': '100',
                'sort': [
                    {
                        'field': 'updated_on_to_order',
                        'order': 'desc'
                    }
                ]
            }
        }
    ]

    queries = []

    url = 'https://api.revolico.app/graphql/'

    start_urls = [
        'compra-venta',
        'empleos',
        'autos',
        'servicios',
        'vivienda',
        'computadoras',
    ]

    for start_url in start_urls:
        q = deepcopy(query)
        q[0]['variables']['categorySlug'] = start_url
        queries.append(q)

    def start_requests(self):
        for query in self.queries:
            yield Request(self.url, method='POST', dont_filter=True, errback=self.on_error,
                          body=json.dumps(query),
                          headers={'Content-Type': 'application/json'},
                          meta={"query": query}
                          )

    def parse(self, response):
        query = response.meta['query']
        results = json.loads(response.body)
        page_info = results[0]['data']['adsPerPage']['pageInfo']
        ads = results[0]['data']['adsPerPage']['edges']

        for ad_node in ads:
            yield self.parser.parse_ad(ad_node['node'])

        if page_info['hasNextPage'] and self.depth > 0:
            query[0]['variables']['page'] = query[0]['variables']['page'] + 1
            self.depth -= 1
            yield response.follow(self.url, method='POST', callback=self.parse,
                                  body=json.dumps(query),
                                  headers={'Content-Type': 'application/json'},
                                  meta={"query": query}
                                  )
