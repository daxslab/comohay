# -*- coding: utf-8 -*-
from haystack.backends.whoosh_backend import WhooshEngine, WhooshSearchBackend
from whoosh.analysis import CharsetFilter, StemmingAnalyzer, StopFilter
# from whoosh.support.charset import accent_map
from whoosh.fields import TEXT

from utils.spanish_stemmer import SpanishStemmer

STOPWORDS = [
    'tenidos', 'habidas', 'tendré', 'tendrán', 'antes', 'suyo', 'nosotras', 'porque', 'durante', 'él', 'sí', 'nada',
    'seremos', 'desde', 'vosotras', 'una', 'tenemos', 'están', 'tenías', 'le', 'habríamos', 'tengamos', 'estoy', 'seas',
    'estaríais', 'estará', 'hubieseis', 'serías', 'y', 'te', 'habiendo', 'contra', 'hubiesen', 'fueses', 'todo', 'sentidas',
    'sentida', 'serían', 'ni', 'tuvieron', 'lo', 'tendrías', 'está', 'tuvo', 'algunas', 'tenéis', 'estarían', 'tienen',
    'tuvierais', 'esa', 'estaban', 'otra', 'suya', 'tus', 'estaríamos', 'los', 'tenga', 'tuvieseis', 'mías', 'estaba',
    'estaremos', 'tengo', 'estada', 'nuestra', 'de', 'que', 'tuya', 'estad', 'estuviera', 'esas', 'algo', 'estas', 'tanto',
    'estés', 'haya', 'tuviesen', 'fuera', 'habrán', 'tuve', 'quien', 'seréis', 'un', 'sentidos', 'habríais', 'hayan', 'había',
    'estuvo', 'muchos', 'yo', 'otro', 'tendría', 'habría', 'estamos', 'vuestros', 'tienes', 'estar', 'cuando', 'estás',
    'fueran', 'tendríais', 'ese', 'hubieran', 'fueron', 'estuvisteis', 'estuviesen', 'uno', 'esta', 'tengas', 'vuestro',
    'eran', 'tendréis', 'seríamos', 'has', 'esos', 'tenían', 'serán', 'son', 'o', 'éramos', 'hubieses', 'estáis', 'tuviese',
    'las', 'mis', 'seríais', 'les', 'será', 'hubiésemos', 'la', 'fuésemos', 'estarán', 'mucho', 'habremos', 'habréis',
    'habíamos', 'serás', 'otras', 'hubierais', 'hubo', 'pero', 'estadas', 'se', 'sus', 'fuimos', 'vosotros', 'suyos',
    'habíais', 'habré', 'donde', 'hayamos', 'tuviéramos', 'tú', 'estemos', 'estuvieses', 'habidos', 'tiene', 'esté', 'fui',
    'estuve', 'el', 'estarás', 'ha', 'mi', 'estuviéramos', 'eres', 'estuvimos', 'todos', 'fuerais', 'otros', 'quienes',
    'sin', 'nosotros', 'estuviésemos', 'seré', 'también', 'me', 'ti', 'tuvieses', 'con', 'tuvisteis', 'no', 'estuvieran',
    'e', 'por', 'habías', 'estado', 'para', 'hay', 'entre', 'estaré', 'seamos', 'tendremos', 'habían', 'tengan', 'vuestra',
    'tuyas', 'tengáis', 'siente', 'estaría', 'a', 'fuiste', 'tuviste', 'fuesen', 'sentid', 'fuisteis', 'al', 'estén', 'cual',
    'tuvieras', 'tened', 'estos', 'estuvieron', 'hube', 'estuviese', 'habrían', 'estabais', 'tuvimos', 'nuestras', 'ante',
    'hubiéramos', 'algunos', 'fuéramos', 'eso', 'tuvieran', 'tendrás', 'ellas', 'nos', 'tu', 'tenida', 'vuestras', 'eras',
    'teníais', 'esto', 'habida', 'sois', 'mí', 'tendrá', 'estuvieras', 'más', 'tuviera', 'os', 'sea', 'habéis', 'soy', 'qué',
    'nuestros', 'hubiste', 'hubiera', 'teniendo', 'tuyo', 'es', 'tenidas', 'hayas', 'estabas', 'estados', 'sean', 'tendrían',
    'ellos', 'su', 'hemos', 'tuyos', 'somos', 'fueras', 'era', 'suyas', 'hubieron', 'en', 'mío', 'hubimos', 'tenía', 'teníamos',
    'habrías', 'estando', 'sintiendo', 'estarías', 'estábamos', 'estuviste', 'han', 'he', 'mía', 'sería', 'erais', 'habrás',
    'estuvieseis', 'fueseis', 'como', 'habido', 'hubieras', 'poco', 'fuese', 'estaréis', 'del', 'míos', 'tenido', 'sobre',
    'estéis', 'estuvierais', 'seáis', 'tendríamos', 'hubiese', 'hayáis', 'sentido', 'este', 'ya', 'hubisteis', 'muy', 'nuestro',
    'ella', 'fue', 'habrá', 'unos', 'tuviésemos', 'hasta'
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
