# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q

from ads.models import Ad
from comohay import settings


class RemoveDuplicatedAdPipeline(object):

    def process_item(self, item, spider):

        if spider.name != 'hogarencuba': # hogarencuba has no duplicates
            try:
                # Remove duplicated ads from same contact
                a = Q(contact_email=item['contact_email']) & Q(contact_email__isnull=False) & ~Q(contact_email__exact='')
                b = Q(contact_phone=item['contact_phone']) & Q(contact_phone__isnull=False) & ~Q(contact_phone__exact='')
                Ad.objects.annotate(
                    desc_similarity=TrigramSimilarity('description', item['description'])
                ).filter(
                    a or b
                ).filter(
                    desc_similarity__gt=settings.DESCRIPTION_SIMILARITY,
                ).exclude(
                    external_source=item['external_source'],
                    external_id=item['external_id']
                ).delete()

                ## Remove duplicated ads
                # Ad.objects.annotate(
                #     title_similarity=TrigramSimilarity('title', item['title']),
                #     desc_similarity=TrigramSimilarity('description', item['description'])
                # ).filter(
                #     external_source=item['external_source'],
                #     title_similarity__gt=settings.TITLE_SIMILARITY,
                #     desc_similarity__gt=settings.DESCRIPTION_SIMILARITY).delete()
            except Exception as e:
                logging.error("Error removing duplicated items: "+str(e))
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
            instance.slug = ad.slug
            instance.created_at = ad.created_at
            instance.updated_at = ad.updated_at
            instance.created_by = ad.created_by
            instance.updated_by = ad.updated_by
            instance.pk = ad.pk
        except Ad.DoesNotExist:
            pass
        return item

    def process_item(self, item, spider):
        item = self._preprocess_ad_item(item)
        item.save()
        return item