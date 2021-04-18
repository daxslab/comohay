from datetime import timedelta, datetime

from actstream.models import Action
from django.core.management.base import BaseCommand
from django.utils import timezone

from ads.models import User


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', default=15, type=int,
            help='Number of days without log in for cleanup')

    def handle(self, *args, **options):

        anonymous_user = User.objects.filter(username='anonymous').get()

        now = timezone.now()
        days = options['days']
        days_delta = timedelta(days)

        old_users = User.objects.select_related('lazyuser').filter(
            lazyuser__id__gt=0,
            last_login__lt=now - days_delta
        ).order_by('id').all().iterator()

        for old_user in old_users:
            Action.objects.filter(actor_object_id=old_user.id).update(actor_object_id=anonymous_user.id)
            old_user.delete()
