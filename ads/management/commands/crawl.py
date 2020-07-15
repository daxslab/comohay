import sys

from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from comohay import settings


class Command(BaseCommand):
    help = "Release the spiders"

    def add_arguments(self, parser):
        parser.add_argument(
            'source',
            nargs='?',
            help='Source to load (default loads all source)',
        )
        parser.add_argument(
            '--depth', default=4, type=int,
            help='How depth recursively search in sites')

    def handle(self, *args, **options):

        if options['source']:
            if settings.EXTERNAL_SOURCES.get(options['source'], None):
                sources = {options['source']: settings.EXTERNAL_SOURCES[options['source']]}
            else:
                self.logger.error('La fuente seleccionada "%s" no está definida', options['source'])
                sys.exit(2)
        else:
            sources = settings.EXTERNAL_SOURCES


        process = CrawlerProcess(get_project_settings())

        for source in sources:
            process.crawl(source, depth=options['depth'])
        process.start()