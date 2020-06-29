import logging

from django.core.management.base import BaseCommand
from django.db import models

from ads.models import Ad


class Command(BaseCommand):
    logger = logging.getLogger('console')

    def handle(self, *args, **options):
        self.remove_duplicated_records()

    def remove_duplicated_records(self):
        """
        Removes records from `model` duplicated on `fields`
        while leaving the most recent one (biggest `id`).
        """
        fields = ('title', 'description')
        duplicates = Ad.objects.values(*fields).filter(external_source__isnull=False)

        # override any model specific ordering (for `.annotate()`)
        duplicates = duplicates.order_by()

        # group by same values of `fields`; count how many rows are the same
        duplicates = duplicates.annotate(
            max_id=models.Max("id"), count_id=models.Count("id")
        )

        # leave out only the ones which are actually duplicated
        duplicates = duplicates.filter(count_id__gt=1)

        for duplicate in duplicates:
            to_delete = Ad.objects.filter(**{x: duplicate[x] for x in fields})

            # leave out the latest duplicated record
            # you can use `Min` if you wish to leave out the first record
            to_delete = to_delete.exclude(id=duplicate["max_id"])

            to_delete.delete()

