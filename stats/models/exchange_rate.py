from django.db import models


class ExchangeRate(models.Model):
    TYPE_BUY = 'buy'
    TYPE_SELL = 'sell'
    TYPE_MID = 'mid'
    TYPES = ((TYPE_BUY, 'Buy price'), (TYPE_SELL, 'Sell price'), (TYPE_MID, 'Mid price'))
    source_currency_iso = models.CharField(max_length=3)
    target_currency_iso = models.CharField(max_length=3)
    type = models.CharField(max_length=10, choices=TYPES)
    wavg = models.DecimalField(max_digits=14, decimal_places=8)
    max = models.DecimalField(max_digits=14, decimal_places=8)
    min = models.DecimalField(max_digits=14, decimal_places=8)
    ads_qty = models.IntegerField()
    datetime = models.DateTimeField()
