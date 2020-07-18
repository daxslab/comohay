import datetime

from django.db.models import Count, Min
from haystack import indexes

from ads.models import UserSearch, Search
from ads.models.ad import Ad
from datetime import datetime, timezone


class AdIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title', boost=1.125)
    description = indexes.CharField(model_attr='description')
    price = indexes.DecimalField(model_attr='price')
    province = indexes.CharField(model_attr='province__name', boost=1.120)
    municipality = indexes.CharField(model_attr='municipality__name')

    updated_at = indexes.DateTimeField(model_attr='updated_at', use_template=False, indexed=False)

    # suggestions = indexes.FacetCharField()

    def get_model(self):
        return Ad

    def prepare(self, object):
        """
        Its super important to avoid to reach a negative number in the boost, with a negative number the
        ranking will be reversed.
        """
        self.prepared_data = super(AdIndex, self).prepare(object)
        self.prepared_data['boost'] = 1 - self.compute_antiquity_penalty(self.prepared_data['updated_at'])
        return self.prepared_data

    def compute_antiquity_penalty(self, updated_at):
        """
        Computes a increasing function given the difference of days between the current date and the updated_at.
        This function never reaches to 1, avoiding this way negatives numbers in document boost.
        """
        diff = datetime.now(timezone.utc) - updated_at
        return 1 - 1 / (1.001 ** diff.days)

    # def index_queryset(self, using=None):
    #     """Used when the entire index for model is updated."""
    #     return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())


# class SearchIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
#     search = indexes.CharField(model_attr='search')
#     rank = indexes.FloatField(model_attr='rank')
#     # autocomplete field
#     content_auto = indexes.EdgeNgramField(model_attr='search')
#
#     def get_model(self):
#         return Search
#
#     def prepare(self, object):
#         self.prepared_data = super(SearchIndex, self).prepare(object)
#         self.prepared_data['boost'] = self.prepared_data['rank'] + 1
#         return self.prepared_data
