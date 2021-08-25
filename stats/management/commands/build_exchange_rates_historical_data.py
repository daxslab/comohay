import datetime

from django.core.management.base import BaseCommand

import stats.exchange_rates_computation_service
from stats.models.exchange_rate import ExchangeRate


class Command(BaseCommand):
    help = "Build EUR, USD and MLC exchange rates historical data."

    start_date_str = '2020-07-01 23:59:00 +00:00'
    # start_date_str = '2021-05-01 23:59:00 +00:00'

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
            ExchangeRate.objects.all().delete()
            current_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
            start_datetime = datetime.datetime.strptime(self.start_date_str, '%Y-%m-%d %H:%M:%S %z')

            while start_datetime <= current_datetime:
                exchange_rates = stats.exchange_rates_computation_service.get_exchange_rates(start_datetime)

                for exchange_rate in exchange_rates:
                    exchange_rate.save()

                self.stdout.write("{datetime} finished.".format(datetime=start_datetime.strftime("%Y-%m-%d %H:%M:%S")))

                start_datetime = start_datetime + datetime.timedelta(days=1)
