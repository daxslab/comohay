import itertools
import re
import datetime
from django.db.models import Q
from ads.models import Ad
import comohay.settings
from currencies.models import CurrencyAd
import logging

logger = logging.getLogger(__name__)

action_regexes = {
    CurrencyAd.TYPE_SALE: ["vendo", "tengo", "en venta", "venta de", "se vende[n]?"],
    CurrencyAd.TYPE_PURCHASE: ["compro", "compra de", "en compra", "se compra[n]?", "necesito", "necesito comprar",
                               "busco",
                               "se busca[n]?"]
}

currencies_regexes = {
    Ad.EURO_ISO: [Ad.EURO_ISO, "euro[s]?"],
    Ad.MLC_ISO: [Ad.MLC_ISO],
    Ad.CANADIAN_DOLLAR_ISO: [Ad.CANADIAN_DOLLAR_ISO, "d[o|ó]lar(?:es)?\s+canadiense[s]?"],
    Ad.MEXICAN_PESO_ISO: [Ad.MEXICAN_PESO_ISO, "peso[s]? mexicano[s]?"],
    Ad.CUBAN_PESO_ISO: [Ad.CUBAN_PESO_ISO, "peso[s]?\s+cubano[s]?", "pesos[s]?", "MN", "moneda nacional"],
    Ad.CONVERTIBLE_CUBAN_PESO_ISO: [Ad.CONVERTIBLE_CUBAN_PESO_ISO, "peso[s]?\s+cubano[s]? convertible[s]?"],
    # USD must always be the last one because otherwise the expression "d[o|ó]lar(?:es)?" could catch "dolares canadienses"
    Ad.AMERICAN_DOLLAR_ISO: [Ad.AMERICAN_DOLLAR_ISO, "d[o|ó]lar(?:es)?\s+americano[s]?", "d[o|ó]lar(?:es)?"],
}

# Excluding CUP and CUC from source currencies
source_currencies_regexes = {currency_iso: regexes for (currency_iso, regexes) in currencies_regexes.items() if
                             currency_iso != Ad.CONVERTIBLE_CUBAN_PESO_ISO and currency_iso != Ad.CUBAN_PESO_ISO}

target_currencies_regexes = currencies_regexes

main_regex = "({ps_rg})\s*\d*\s*({source_curr_rg}){final_word_boundary}(?:en\s*efectivo)?\s*(?:a|en)\s*(\d+[\.,]?\d+)\s(?:({target_curr_rg}){final_word_boundary})?"

regex = main_regex.format(
    ps_rg="|".join([action for sublist in action_regexes.values() for action in sublist]),
    source_curr_rg="|".join(list(itertools.chain.from_iterable(source_currencies_regexes.values()))),
    target_curr_rg="|".join(list(itertools.chain.from_iterable(target_currencies_regexes.values()))),
    final_word_boundary='\\b'
)


def get_currencyad_from_ad(ad: Ad):
    matches = re.match(regex, ad.title, re.IGNORECASE)

    if not matches:
        return None

    # finding the action type (sell or purchase)
    action = None
    for action_type, regexes in action_regexes.items():
        if re.match("^({})$".format("|".join(regexes)), matches.group(1), re.IGNORECASE):
            action = action_type
            break

    # finding the source currency iso
    source_currency_iso = None
    for currency_iso, regexes in source_currencies_regexes.items():
        if re.match("^({})$".format("|".join(regexes)), matches.group(2), re.IGNORECASE):
            source_currency_iso = currency_iso
            break

    # finding the price
    # price = None
    # if matches.group(3):
    #     price = float(matches.group(3).replace(",", "."))
    # elif ad.price:
    #     price = ad.price
    # else:
    #     # if we can't find a price then we have to ignore the ad
    #     return None

    # looking the price only in the title match. There are a lot of human
    # errors in  the price field
    price = None
    if matches.group(3):
        price = float(matches.group(3).replace(",", "."))
    else:
        # if we can't find a price then we have to ignore the ad
        return None

    # finding the target currency iso
    target_currency_iso = None

    # we only look in the title match due to the enormous amount of
    # human errors in the currency_iso field, if there is no currency
    # there, we maintain the default value
    if matches.group(4):
        for currency_iso, regexes in target_currencies_regexes.items():
            if re.match("^({})$".format("|".join(regexes)), matches.group(4), re.IGNORECASE):
                target_currency_iso = currency_iso
                break

    # a very custom identification of target currency. If the target
    # currency wasn't explicit in the message then we have to guess its
    # value based on the date, the source currency and the price.
    if target_currency_iso is None or target_currency_iso == Ad.CUBAN_PESO_ISO:
        # Here we use an estimated date for which the people stopped using CUC as reference,
        # we assume that before that date almost all exchange rate were expressed in CUC
        # values. But as we are not sure of that we are going to use the price to try to
        # guess better. We are 90% sure that before the selected date the price of USD, EUR,
        # MLC or CAD never reached 2 CUC, therefore we are going to use only these source currencies
        # when trying to guess exchange rates in CUC. Hence, we can say that if the ad date is less
        # than the estimated date and the price is less than 2 and the source currency is EUR, USD
        # , MLC or CAD then the target currency is CUC. Otherwise it will be in CUP. It is possible that
        # we get wrong in some ads, but the outliers classifier in the exchange rates computation
        # take care of those anomalous values.
        if ad.external_created_at < datetime.datetime(2021, 3, 1, tzinfo=datetime.timezone.utc) and \
                price < 2 and \
                source_currency_iso in (Ad.EURO_ISO, Ad.AMERICAN_DOLLAR_ISO, Ad.MLC_ISO, Ad.CANADIAN_DOLLAR_ISO):
            target_currency_iso = Ad.CONVERTIBLE_CUBAN_PESO_ISO
        else:
            target_currency_iso = Ad.CUBAN_PESO_ISO

    # if target currency is CUC we convert it to CUP, we don't want CUC in a currencyad
    if target_currency_iso == Ad.CONVERTIBLE_CUBAN_PESO_ISO:
        price = price * comohay.settings.CUC_TO_CUP_CHANGE
        target_currency_iso = Ad.CUBAN_PESO_ISO

    # finding the target currency iso
    # target_currency_iso = Ad.CUBAN_PESO_ISO
    # # if the price was extracted from the title and there is also a currency in the title then we process
    # # that currency
    # if matches.group(3) and matches.group(4):
    #     for currency_iso, regexes in currencies_regexes.items():
    #         if re.match("^({})$".format("|".join(regexes)), matches.group(4), re.IGNORECASE):
    #             target_currency_iso = currency_iso
    # # if there is no price in the title (if there is no price in the title there must be a price in the
    # # price attr, see if block in line 72), then we get the currency from the ad currency_iso
    # elif not matches.group(3):
    #     target_currency_iso = ad.currency_iso

    return CurrencyAd(
        ad=ad,
        type=action,
        source_currency_iso=source_currency_iso,
        target_currency_iso=target_currency_iso,
        price=price
    )


def get_similar_currencyads(currencyad: CurrencyAd):
    ad = currencyad.ad

    currencyads_qs = CurrencyAd.objects.filter(
        source_currency_iso=currencyad.source_currency_iso,
        target_currency_iso=currencyad.target_currency_iso,
        type=currencyad.type
    )

    currencyads_qs = currencyads_qs.filter(
        (Q(ad__contact_phone__isnull=False) & ~Q(ad__contact_phone='') & Q(ad__contact_phone=ad.contact_phone)) |
        (Q(ad__contact_email__isnull=False) & ~Q(ad__contact_email='') & Q(ad__contact_email=ad.contact_email)) |
        (Q(ad__contact_tg__isnull=False) & ~Q(ad__contact_tg='') & Q(ad__contact_tg=ad.contact_tg)) |
        (
                Q(ad__external_contact_id__isnull=False) & ~Q(ad__external_contact_id='') &
                Q(ad__external_source__isnull=False) & ~Q(ad__external_source='') &
                Q(ad__external_contact_id=ad.external_contact_id) & Q(ad__external_source=ad.external_source)
        )
    )

    return currencyads_qs


def get_older_similar_currencyads(currencyad: CurrencyAd):
    return get_similar_currencyads(currencyad).filter(ad__external_created_at__lt=currencyad.ad.external_created_at)


def get_newest_similar_currencyads(currencyad: CurrencyAd):
    return get_similar_currencyads(currencyad).filter(ad__external_created_at__gt=currencyad.ad.external_created_at)


def soft_delete_older_similar_currencyads(currencyad: CurrencyAd):
    for similar_currencyad in get_older_similar_currencyads(currencyad):
        similar_currencyad.ad.delete(soft=True)
        logger.info("Similar older CurrencyAd detected: {}/{} {}".format(
            similar_currencyad.source_currency_iso,
            similar_currencyad.target_currency_iso,
            similar_currencyad.price))
