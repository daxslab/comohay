# -*- coding: utf-8 -*-
from haystack.backends.whoosh_backend import WhooshEngine, WhooshSearchBackend
from whoosh.analysis import CharsetFilter, StemmingAnalyzer, StopFilter
# from whoosh.support.charset import accent_map
from whoosh.fields import TEXT

from utils.spanish_stemmer import SpanishStemmer

STOPWORDS = [
    'y',
    'e',
    'en',
    'ni',
    'no',
    'solo',
    'sino',
    'tambien',
    'siquiera',
    'pero',
    'aunque',
    'al',
    'bien',
    'porque',
    'que',
    'ya',
    'si',
]

class SpanishWhooshSearchBackend(WhooshSearchBackend):

    def build_schema(self, fields):
        schema = super(SpanishWhooshSearchBackend, self).build_schema(fields)
        stemmer_sp = SpanishStemmer()
        stemming_analyzer = StemmingAnalyzer(stemfn=stemmer_sp.stem)

        stop_filter = StopFilter(stoplist=STOPWORDS, minsize=2)

        for name, field in schema[1].items():
            if isinstance(field, TEXT):
                # field.analyzer = StemmingAnalyzer() | CharsetFilter(accent_map)
                field.analyzer = stemming_analyzer | stop_filter

        return schema


class SpanishWhooshEngine(WhooshEngine):
    backend = SpanishWhooshSearchBackend
