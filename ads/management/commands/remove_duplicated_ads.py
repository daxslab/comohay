from django.core.management.base import BaseCommand

from ads.models import Ad
from utils.cli import confirm_input
from ads.services.ad_service import remove_duplicates


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-interaction',
            action='store_true',
            help='Does not wait for user interaction')
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Prints useful info')

    def handle(self, *args, **options):

        if options['no_interaction']:
            user_agree = True
        else:
            print('WARNING: This command starts a heavy long running task that will remove ads from database.')
            user_agree = confirm_input('Do you want to continue? ')

        if user_agree:
            for ad in Ad.objects.all():
                remove_duplicates(ad, verbose=options['verbose'])
