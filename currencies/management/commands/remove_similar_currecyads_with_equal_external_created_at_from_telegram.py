from django.core.management.base import BaseCommand
from django.db.models import Count

from currencies.models import CurrencyAd

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):

        removed_cads_total = 0

        duplicated_cads_values = CurrencyAd.objects.values(
            "source_currency_iso", "target_currency_iso", "type", "ad__contact_tg", "ad__external_created_at"
        ).annotate(count=Count('*')).filter(count__gt=1)

        for cad_values in duplicated_cads_values:

            cad_to_delete_list = CurrencyAd.objects.filter(
                source_currency_iso=cad_values["source_currency_iso"],
                target_currency_iso=cad_values["target_currency_iso"],
                type=cad_values["type"],
                ad__contact_tg=cad_values["ad__contact_tg"],
                ad__external_created_at=cad_values["ad__external_created_at"]
            )

            if cad_to_delete_list.count() > 1:

                logger.info(
                    "Removing {} similar currencyads with its respective ads".format(cad_to_delete_list.count() - 1)
                )

                removed_cads_total += cad_to_delete_list.count() - 1

                for cad_to_delete in cad_to_delete_list[1:]:
                    cad_to_delete.ad.delete(soft=False)

        logger.info("Removed {} curencyads".format(removed_cads_total))
