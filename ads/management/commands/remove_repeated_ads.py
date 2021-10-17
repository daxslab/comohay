from django.core.management.base import BaseCommand
from django.db.models import Count, Sum

from ads.models import Ad
from comohay import settings


class Command(BaseCommand):
    help = "Release the updater spider"

    def handle(self, *args, **options):
        ad_dict_qs = Ad.objects.values('external_url').annotate(count=Count('id')).filter(count__gt=1)

        print("REMOVING {count} duplicates".format(
            count=ad_dict_qs.aggregate(Sum('count'))['count__sum'] - ad_dict_qs.count()
        ))

        for ad_dict in ad_dict_qs:
            ads_to_remove = Ad.objects.filter(external_url=ad_dict['external_url']).order_by('-created_at')[1:]
            print("REMOVING {count} duplicate(s) of {url}".format(count=ads_to_remove.count(), url=ad_dict['external_url']))
            for ad in ads_to_remove:
                ad.delete(soft=False)
