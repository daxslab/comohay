import datetime
from haystack import indexes

from ads.models.ad import Ad


class AdIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    price = indexes.DecimalField(model_attr='price')
    province = indexes.CharField(model_attr='province__name')
    municipality = indexes.CharField(model_attr='municipality__name')

    # autocomplete field
    content_auto = indexes.EdgeNgramField(model_attr='title')

    # suggestions = indexes.FacetCharField()

    def get_model(self):
        return Ad

    # def prepare(self, obj):
    #     prepared_data = super(AdIndex, self).prepare(obj)
    #     prepared_data['suggestions'] = prepared_data['text']
    #     return prepared_data

    # def index_queryset(self, using=None):
    #     """Used when the entire index for model is updated."""
    #     return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())
