import logging
import sys

from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, Max, Min

from ads.models import UserSearch, Search


class Command(BaseCommand):
    logger = logging.getLogger('console')

    def handle(self, *args, **options):
        Search.objects.all().delete()

        searches = UserSearch.objects.values('search').annotate(Count('search'), Avg('daystamp'))
        max_mins = searches.aggregate(Max('search__count'), Min('search__count'), Max('daystamp__avg'),
                                      Min('daystamp__avg'))
        for search in searches:
            rank = self.compute_rank(search, max_mins)
            nsearch = Search(search=search['search'], rank=rank)
            nsearch.save()

    def compute_rank(self, search, max_min_vales):
        search_count_normalized = self.feature_scaling(max_min_vales['search__count__max'],
                                                       max_min_vales['search__count__min'], search['search__count'])
        daystamp_avg_normalized = self.feature_scaling(max_min_vales['daystamp__avg__max'],
                                                       max_min_vales['daystamp__avg__min'], search['daystamp__avg'])

        return (search_count_normalized + daystamp_avg_normalized) / 2

    @staticmethod
    def feature_scaling(max_value, min_value, value):
        return (value - min_value) / (max_value - min_value) if max_value != min_value else 1
