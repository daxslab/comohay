from django.core.management.base import BaseCommand
import itertools
import re

from ads import currencyad_service
from ads.models import Ad, CurrencyAd


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-prompt',
            action='store_true',
            help='Not show confirmation prompt',
        )

    def handle(self, *args, **options):

        allow = True

        if not options['no_prompt']:
            result = input(
                "The whole history will be removed and computed again. Are you sure you want to proceed? (y/n)")

            while len(result) < 1 or result[0].lower() not in "yn":
                result = input("Please answer \"y\" or \"n\"")

            allow = result[0].lower() == "y"

        if allow:

            CurrencyAd.objects.all().delete()

            final_regex = currencyad_service.main_regex.format(
                ps_rg="|".join([action for sublist in currencyad_service.action_regexes.values() for action in sublist]),
                curr_rg="|".join(list(itertools.chain.from_iterable(currencyad_service.currencies_regexes.values()))),
                target_curr_rg="|".join(list(itertools.chain.from_iterable(currencyad_service.currencies_regexes.values()))),
                final_word_boundary="\\M"
            )

            ads = Ad.objects.raw("SELECT *, regexp_matches(title, '{regex}', 'i') as regexp_matches FROM ads_ad ORDER BY external_created_at ASC".format(regex=final_regex))

            for ad in ads:
                currencyad = currencyad_service.get_currencyad_from_ad(ad)
                if currencyad:
                    currencyad.save()



