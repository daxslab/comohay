import datetime

from haystack import indexes

from ads.models.ad import Ad
from datetime import datetime, timezone

from haystack_custom import fields


class AdIndex(indexes.SearchIndex, indexes.Indexable):
    text = fields.CharField(document=True, use_template=True, extra_attr={"omitNorms": "true"})

    title = fields.CharField(model_attr='title', extra_attr={"omitNorms": "true"})

    description = fields.CharField(model_attr='description', extra_attr={"omitNorms": "true"})

    price = fields.TFloatField(model_attr='price')

    currency_iso = fields.CharField(model_attr='currency_iso',
                                    extra_attr={"omitNorms": "true", "omitTermFreqAndPositions": "true"})

    province = fields.CharField(model_attr='province__name',
                                extra_attr={"omitNorms": "true"})

    municipality = fields.CharField(model_attr='municipality__name',
                                    extra_attr={"omitNorms": "true", "omitTermFreqAndPositions": "true"})

    # used for boosting
    external_created_at = fields.DateTimeField(model_attr='external_created_at', null=True, default=datetime.min,
                                               extra_attr={"omitNorms": "true"})

    # used for extract similar ads
    description_length = indexes.IntegerField(use_template=False, indexed=False, stored=True)

    title_length = indexes.IntegerField(use_template=False, indexed=False, stored=True)

    is_deleted = indexes.BooleanField(model_attr='is_deleted', use_template=False, indexed=True, stored=True)

    def get_model(self):
        return Ad

    def prepare(self, object):
        """
        Its super important to avoid to reach a negative number in the boost, with a negative number the
        ranking will be reversed.
        """
        self.prepared_data = super(AdIndex, self).prepare(object)
        self.prepared_data['description_length'] = len(self.prepared_data['description'])
        self.prepared_data['title_length'] = len(self.prepared_data['title'])

        return self.prepared_data

    def compute_antiquity_penalty(self, updated_at):
        """
        Computes a increasing function given the difference of days between the current date and the updated_at.
        This function never reaches to 1, avoiding this way negatives numbers in document boost.
        """
        diff = datetime.now(timezone.utc) - updated_at
        return 1 - 1 / (1.001 ** diff.days)
