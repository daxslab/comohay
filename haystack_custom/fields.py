from haystack.fields import NgramField


class TrigramField(NgramField):
    field_type = "trigram"
