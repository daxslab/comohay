import sys

from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from comohay import settings
from scraper.spiders.hogarencuba import HogarencubaSpider
from scraper.spiders.revolico import RevolicoSpider


class Command(BaseCommand):
    help = "update proxy list"

    def handle(self, *args, **options):

        process = CrawlerProcess(get_project_settings())
        process.crawl('proxycrawler')
        process.start()