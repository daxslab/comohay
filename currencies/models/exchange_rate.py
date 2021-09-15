from django.db import models


class ExchangeRate(models.Model):

    # IMPORTANT NOTE:
    #   The values of mad and median refers to the Mean Absolute Deviation
    #   and the mean used to detect the outliers before computing the exchange
    #   rate. Therefore their values refers to the whole dataset of currencyads,
    #   in contrast with wavg, max and min that are computed after removing the
    #   outliers.

    TYPE_BUY = 'buy'
    TYPE_SELL = 'sell'
    TYPE_MID = 'mid'
    TYPES = ((TYPE_BUY, 'Buy price'), (TYPE_SELL, 'Sell price'), (TYPE_MID, 'Mid price'))
    source_currency_iso = models.CharField(max_length=3)
    target_currency_iso = models.CharField(max_length=3)
    type = models.CharField(max_length=10, choices=TYPES)
    wavg = models.FloatField()
    max = models.FloatField()
    min = models.FloatField()
    mad = models.FloatField()
    median = models.FloatField()
    days_span = models.IntegerField()
    deviation_threshold = models.FloatField()
    ads_qty = models.IntegerField()
    datetime = models.DateTimeField()
