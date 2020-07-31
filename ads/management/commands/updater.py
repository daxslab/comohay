from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from comohay import settings


class Command(BaseCommand):
    help = "Release the updater spider"

    def add_arguments(self, parser):

        parser.add_argument(
            '-s', '--source',
            nargs='+',
            help='Set updater sources to check',
            required=False
        )

        parser.add_argument(
            '-p', '--update-period', type=int, default=settings.AD_UPDATE_PERIOD,
            help='Number of days that updater spider look for updates in an ad')

    def handle(self, *args, **options):

        process = CrawlerProcess(get_project_settings())

        process.crawl('updater', source=options['source'], update_period=options['update_period'])
        process.start()