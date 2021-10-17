# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime

from django.db.models import Q
from django.utils import timezone
from scrapy.exceptions import DropItem

from ads.models import Ad
from ads.services.ad_service import remove_duplicates, has_duplicates
from ads.tasks import broadcast_in_telegram
from currencies.models import CurrencyAd
from currencies.services import currencyad_service
import currencies.services.currencyad_service


# This pipeline is not in use right now, the duplicate detection is being made in the BaseAdPipeline pipeline
from scraper.items import AdItem


class RemoveDuplicatedAdPipeline(object):

    def process_item(self, item, spider):

        if spider.name not in ['hogarencuba', 'updater'] and item['description'].strip() != '':  # hogarencuba has no duplicates and updater only updates
            remove_duplicates(item.save(commit=False))

        return item


class BaseAdPipeline(object):

    def process_item(self, item: AdItem, spider):

        ad = item.save(commit=False)

        currencyad = currencies.services.currencyad_service.get_currencyad_from_ad(ad)
        if currencyad:
            # if the currencyad is an exact duplicate OR there is a similar newer
            # currency ad that makes it obsolete then raise a drop item
            if Ad.objects.filter(external_url=ad.external_url).count() > 0 or \
                    currencyad_service.get_newest_similar_currencyads(currencyad).count() > 0:
                raise DropItem()

            # otherwise mark as deleted the older similar ones
            currencyad_service.soft_delete_older_similar_currencyads(currencyad)

            ad.save()
            currencyad.save()
            is_new_ad = True

        else:
            # if the ad is not a currencyad then treat it as a normal ad
            if Ad.objects.filter(external_url=ad.external_url).count() > 0 or has_duplicates(ad):
                # in theory it can be only one duplicate. If the duplicate is the same ad,
                # we're going to update it, otherwise we drop the incoming ad.

                # It is necessary to update the duplicate ad in case it is the same no matter
                # the existence of a check based on the external_url that is made before
                # requesting the ad source (see line 33 of scraper/spiders/uncuc.py) for
                # reference. This additional updating step is useful because the ad could
                # have changed its external url in its source but not its external_id,
                # therefore the parser will request the new ad url and when the ad is
                # passing through this method it will find that the ad was in db due to the
                # external_id and instead af adding it as a new ad it will just update it
                try:
                    # looking for the same ad in db
                    original_ad = Ad.objects.get(
                        external_source=item['external_source'],
                        external_id=item['external_id']
                    )

                    # Already exists, just update it
                    ad.id = original_ad.id
                    ad.slug = original_ad.slug
                    ad.created_at = original_ad.created_at
                    ad.updated_at = timezone.now()
                    ad.created_by = original_ad.created_by
                    ad.updated_by = original_ad.updated_by

                    # Update external_created_at only if it doesn't have value in the incoming ad
                    if not ad.external_created_at and original_ad.external_created_at:
                        ad.external_created_at = original_ad.external_created_at

                    ad.pk = original_ad.pk

                except Ad.DoesNotExist:
                    raise DropItem()

            is_new_ad = True if ad.id is None else False
            ad = item.save()

        if is_new_ad:
            broadcast_in_telegram.apply_async((ad.id,), retry=True)

        return item
