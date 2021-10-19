import logging
import sys

from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from ads.models import Ad
from comohay import settings

logger = logging.getLogger('main')


class Command(BaseCommand):

    def handle(self, *args, **options):
        ads_to_remove = Ad.objects.filter(external_source='bachecubano.com', is_deleted=False)
        print("Removing {count} ads".format(count=ads_to_remove.count()))
        for ad_to_remove in ads_to_remove:
            ad_to_remove.delete(soft=True)
            print("Removed ad with id {id}".format(id=ad_to_remove.id))
