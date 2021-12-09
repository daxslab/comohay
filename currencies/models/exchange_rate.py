from django.db import models
import datetime


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


class ActiveExchangeRate:
    def __init__(
            self,
            source_currency_iso: str,
            target_currency_iso: str,
            buy_exchange_rate: ExchangeRate = None,
            sell_exchange_rate: ExchangeRate = None,
            mid_exchange_rate: ExchangeRate = None,
            target_datetime: datetime.datetime = None
    ) -> None:
        super().__init__()
        self.source_currency_iso = source_currency_iso
        self.target_currency_iso = target_currency_iso
        self.buy_exchange_rate = buy_exchange_rate
        self.sell_exchange_rate = sell_exchange_rate
        self.mid_exchange_rate = mid_exchange_rate
        self.target_datetime = target_datetime
