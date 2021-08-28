import sys

from haystack.backends import SQ
from haystack.forms import ModelSearchForm
from haystack.inputs import AutoQuery, Raw, AltParser, Clean

from ads.models import Ad, Province
from django import forms

from comohay import settings
from utils.remove_duplicates import double_clean


class AdSearchForm(ModelSearchForm):
    provinces = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Province.objects.all(),
        to_field_name='name'
    )

    price_from = forms.IntegerField(required=False)
    price_to = forms.IntegerField(required=False)
    price_currency = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sqs = None

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            return self.no_query_found()

        q = self.cleaned_data['q']

        provinces = self.cleaned_data['provinces']
        price_from = self.cleaned_data['price_from']
        price_to = self.cleaned_data['price_to']
        price_currency = self.cleaned_data['price_currency']

        # boosting of 1.5 for every term that appears in the title
        # TODO: improve this by overriding the solr backend method build_alt_parser_query in order to avoid to do the
        #  escaping twice. It will be recommended in order to avoid triple escaping in the boost query(bq) to build the
        #  query with the defType parameter instead of the LocalParams syntax that is currently being in use by the
        #  build_alt_parser_query method.
        bq = self.create_boosting_query(q)

        # boost multiplier by age. This solr function will return a number between 1 an 0, the older the ad the lower
        # the number. Please refer to
        #   https://lucene.apache.org/solr/guide/7_7/function-queries.html
        #   https://lucene.apache.org/core/6_6_0/queries/org/apache/lucene/queries/function/valuesource/ReciprocalFloatFunction.html and
        #   https://www.youtube.com/watch?v=3E8jOUgj6L8to
        boost = "recip(ms(NOW,external_created_at),3.16e-11,1,1)"

        pf = "title^2.5 description^0.15"
        pf3 = "title^1.5 description^0.10"
        pf2 = "title^0.5 description^0.05"

        sqs = self.searchqueryset.filter(
            content=AltParser('edismax', q, bq=bq, boost=boost, pf=pf, pf3=pf3, pf2=pf2, ps=2, ps3=2, ps2=1))

        if provinces.count() > 0:
            sqs = sqs.filter_and(province__in=provinces.values_list('name', flat=True))

        if price_from and price_to:
            sqs = sqs.filter_and(price__range=[price_from, price_to])
        elif price_from:
            sqs = sqs.filter_and(price__range=[price_from, sys.maxsize])
        elif price_to:
            sqs = sqs.filter_and(price__range=[0, price_to])

        if price_from or price_to:
            sqs = sqs.filter_and(currency_iso=price_currency)

        if self.load_all:
            sqs = sqs.load_all()

        return sqs.models(Ad)

    def create_boosting_query(self, query):
        # Removing '"' because its not necessary for query boosting
        query = query.replace('"', '')

        clean_q = self.triple_clean(query)
        clean_q = clean_q.replace("'", "\\\\'")

        # this will add the field to search and the boosting value for each term.
        # Eg. 'split royal' -> 'title:split^1.5 title:royal^1.5 description:split^1.1 description:royal^1.1'
        return 'title:' + clean_q.replace(' ', '^1.5 title:') + '^1.5' + ' description:' + clean_q.replace(' ',
                                                                                                           '^0.1 description:') + '^0.1'

    def triple_clean(self, query_fragment):
        """
        Provides a mechanism for sanitizing user input before presenting the
        value to the backend.

        A basic (override-able) implementation is provided.
        """
        backend = self.searchqueryset.query.backend

        if not isinstance(query_fragment, str):
            return query_fragment

        words = query_fragment.split()
        cleaned_words = []

        for word in words:
            if word in backend.RESERVED_WORDS:
                word = word.replace(word, word.lower())

            for char in backend.RESERVED_CHARACTERS:
                word = word.replace(char, "\\\\\\\\%s" % char)

            cleaned_words.append(word)

        return " ".join(cleaned_words)
