from haystack import fields


class CharField(fields.CharField):
    extra_attr = {}

    def __init__(self, **kwargs, ):
        if kwargs.get("extra_attr"):
            self.extra_attr = kwargs.get("extra_attr")
            del kwargs['extra_attr']
        super().__init__(**kwargs)


class DateTimeField(fields.DateTimeField):
    extra_attr = {}
    field_type = "tdate"

    def __init__(self, **kwargs, ):
        if kwargs.get("extra_attr"):
            self.extra_attr = kwargs.get("extra_attr")
            del kwargs['extra_attr']
        super().__init__(**kwargs)


class TFloatField(fields.FloatField):
    extra_attr = {}
    field_type = "tfloat"

    def __init__(self, **kwargs, ):
        if kwargs.get("extra_attr"):
            self.extra_attr = kwargs.get("extra_attr")
            del kwargs['extra_attr']
        super().__init__(**kwargs)
