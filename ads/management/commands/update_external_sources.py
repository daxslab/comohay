import logging
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string


class Command(BaseCommand):

    help = 'Load data from external sources'

    logger = logging.getLogger('console')

    def add_arguments(self, parser):
        parser.add_argument(
            'source',
            nargs='?',
            help='Source to load (default loads all source)',
        )

    def handle(self, *args, **options):
        if options['source']:
            if settings.EXTERNAL_SOURCES.get(options['source'], None):
                sources = {options['source']: settings.EXTERNAL_SOURCES[options['source']]}
            else:
                self.logger.error('La fuente seleccionada "%s" no está definida', options['source'])
                sys.exit(2)
        else:
            sources = settings.EXTERNAL_SOURCES
        for source in sources:
            importer = import_string(sources[source])()
            importer.run()
