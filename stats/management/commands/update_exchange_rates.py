from django.core.management.base import BaseCommand
from django.forms import model_to_dict
import stats.exchange_rates_computation_service


class Command(BaseCommand):
    help = "Compute EUR, USD and MLC exchange rates."

    def handle(self, *args, **options):
        exchange_rates = stats.exchange_rates_computation_service.update_exchange_rates()
        self.stdout.write("Computed Exchange Rates:")
        for exchange_rate in exchange_rates:
            self.stdout.write(model_to_dict(exchange_rate).__str__())
