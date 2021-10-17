from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from comohay import settings


class Command(BaseCommand):
    help = "Release the updater spider"

    def add_arguments(self, parser):

        parser.add_argument(
            '-s', '--sources',
            nargs='+',
            help='Set updater sources to check',
            required=False
        )

        parser.add_argument(
            '-t', '--update-type', type=str, default='all',
            help='Type of the ads to update: all, currencyads, non-currencyads')

    def handle(self, *args, **options):

        process = CrawlerProcess(get_project_settings())

        process.crawl('updater', sources=options['sources'], update_type=options['update_type'])
        process.start()