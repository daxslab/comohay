from django.core.management.base import BaseCommand

from utils.cli import confirm_input
from utils.detect_similarity import detect_similarity

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--similarity', default=0.7, type=float,
            help='Define similarity limit',
        )
        parser.add_argument(
            '--chars', default=1000, type=int,
            help='Limit of characters of Ad description to analise')
        parser.add_argument(
            '--days', default=3, type=int,
            help='Days limit for ads analysis')
        parser.add_argument(
            '--safe',
            action='store_true',
            help='Just prints the ads checked for deletion')
        parser.add_argument(
            '--no-interaction',
            action='store_true',
            help='Does not wait for user interaction')

    def handle(self, *args, **options):

        if options['no_interaction']:
            user_agree = True
        else:
            print('WARNING: This command starts a heavy long running task that will remove ads from database.')
            user_agree = confirm_input('Do you want to continue? ')

        if user_agree:
            duplicates = detect_similarity(options['similarity'], options['chars'], options['days'])
            for element in duplicates:
                if options['safe']:
                    print(element.id, element)
                else:
                    element.delete()
