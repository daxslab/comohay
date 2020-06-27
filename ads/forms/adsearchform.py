from haystack.forms import ModelSearchForm

from ads.models import Ad


class AdSearchForm(ModelSearchForm):
    def search(self):
        sqs = super(ModelSearchForm, self).search()
        return sqs.models(Ad)
