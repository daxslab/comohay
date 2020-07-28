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

from ads.models import Ad
from comohay import settings


class RemoveDuplicatedAdPipeline(object):

    def process_item(self, item, spider):

        if spider.name not in ['hogarencuba', 'updater'] and item['description'].strip() != '':  # hogarencuba has no duplicates and updater only updates
            sqs = SearchQuerySet()
            clean_desc = sqs.query.clean(item['description'])
            similarity = int(settings.DESCRIPTION_SIMILARITY * 100)
            max_len = len(item['description']) + int(len(item['description']) * settings.DESCRIPTION_LENGTH_DIFF)
            ids_values = sqs.filter(
                content=Raw("(description_length:[0 TO {}]) AND {{!dismax qf=description mm={}%}}{}".format(max_len, similarity, clean_desc,))
            ).values_list('id')
            ids = list(map(lambda x: x[0].split('.')[-1], ids_values))

            try:
                # Remove duplicated ads from same contact

                a = Q(id__in=ids)
                b = Q(contact_email=item['contact_email']) & Q(contact_email__isnull=False) & ~Q(
                    contact_email__exact='')
                c = Q(contact_phone=item['contact_phone']) & Q(contact_phone__isnull=False) & ~Q(
                    contact_phone__exact='')
                d = Q(external_contact_id=item['external_contact_id']) \
                    & Q(external_contact_id__isnull=False) \
                    & ~Q(external_contact_id__exact='') \
                    & Q(external_source=item['external_source'])

                Ad.objects.filter(
                    a & (b | c | d)
                ).exclude(
                    external_source=item['external_source'],
                    external_id=item['external_id']
                ).delete()

            except Exception as e:
                logging.error("Error removing duplicated items: " + str(e))
        return item


class BaseAdPipeline(object):

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
        item = self._preprocess_ad_item(item)
        item.save()
        return item