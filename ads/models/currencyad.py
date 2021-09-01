from django.db import models
from ads.models import Ad


class CurrencyAd(models.Model):
    TYPE_SALE = "sale"
    TYPE_PURCHASE = "purchase"
    ALLOWED_TYPES = ((TYPE_SALE, "Sale"), (TYPE_PURCHASE, 'Purchase'))

    # the same currencies in Ads but without CUC
    ALLOWED_CURRENCIES = [currency for currency in Ad.ALLOWED_CURRENCIES if
                          currency[0] != Ad.CONVERTIBLE_CUBAN_PESO_ISO]

    ad = models.ForeignKey(to=Ad, on_delete=models.CASCADE)
    type = models.CharField(max_length=9, choices=ALLOWED_TYPES)
    source_currency_iso = models.CharField(max_length=3, choices=ALLOWED_CURRENCIES)
    target_currency_iso = models.CharField(max_length=3, choices=ALLOWED_CURRENCIES)
    price = models.FloatField()
