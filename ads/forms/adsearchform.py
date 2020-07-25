from haystack.backends import SQ
from haystack.forms import ModelSearchForm
from haystack.inputs import AutoQuery, Raw

from ads.models import Ad


class AdSearchForm(ModelSearchForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sqs = None

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            return self.no_query_found()

        q = self.cleaned_data['q']

        # This is a hack because it seems that hasytack doesnt know solr uses OR operator by default
        # processed_query = q.replace(' ', ' AND ')
        # processed_query = '({})'.format(processed_query)
        #
        # self.sqs = self.searchqueryset.filter(
        #     SQ(content=Raw(processed_query)) | SQ(title=AutoQuery(q)) | SQ(province=AutoQuery(q)))

        self.sqs = self.searchqueryset.filter(
            SQ(content=AutoQuery(q)) | SQ(title=AutoQuery(q)))

        # self.sqs = self.searchqueryset.auto_query(self.cleaned_data["q"])

        if self.load_all:
            self.sqs = self.sqs.load_all()

        return self.sqs.models(Ad)
