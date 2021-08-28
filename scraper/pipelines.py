# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.utils import timezone
from haystack.inputs import Raw
from haystack.query import SearchQuerySet
from scrapy.exceptions import DropItem

from ads.models import Ad
from comohay import settings
from utils.remove_duplicates import remove_duplicates, has_duplicates
from ads.tasks import broadcast_in_telegram


# This pipeline is not in use right now, the duplicate detection is being made in the BaseAdPipeline pipeline
class RemoveDuplicatedAdPipeline(object):

    def process_item(self, item, spider):

        if spider.name not in ['hogarencuba', 'updater'] and item['description'].strip() != '':  # hogarencuba has no duplicates and updater only updates
            remove_duplicates(item.save(commit=False))

        return item


class BaseAdPipeline(object):

    # used for update the incoming ad, this is necessary no matter the existence of a check based on the external_url
    # that is made before requesting the ad source (see line 33 of scraper/spiders/uncuc.py) for reference.
    # This additional updating step is useful because the ad could have changed its external url in its source but not
    # its external_id, therefore the parser will request the new ad url and when the ad is passing through this method
    # it will find that the ad was in db due to the external_id and instead af adding it as a new ad it will just update
    # it
    def _preprocess_ad_item(self, item):
        try:
            ad = Ad.objects.get(
                external_source=item['external_source'],
                external_id=item['external_id']
            )
            # Already exists, just update it
            instance = item.save(commit=False)
            instance.id = ad.id
            instance.slug = ad.slug
            instance.created_at = ad.created_at
            instance.updated_at = timezone.now()
            instance.created_by = ad.created_by
            instance.updated_by = ad.updated_by
            # Doesn't update external_created_at if has no new value
            if not instance.external_created_at and ad.external_created_at:
                instance.external_created_at = ad.external_created_at

            instance.pk = ad.pk
        except Ad.DoesNotExist:
            pass
        return item

    def process_item(self, item, spider):
        if has_duplicates(item.save(commit=False)):
            raise DropItem()

        item = self._preprocess_ad_item(item)

        is_new_ad = True if item.instance.id is None else False

        ad = item.save()

        if is_new_ad:
            broadcast_in_telegram.apply_async((ad.id,), retry=True)

        return item
