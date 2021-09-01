import itertools
import re
import datetime

from ads.models import Ad, CurrencyAd
from stats import exchange_rates_computation_service
import comohay.settings

action_regexes = {
    CurrencyAd.TYPE_SALE: ["vendo", "tengo", "en venta", "venta de", "se vende[n]?"],
    CurrencyAd.TYPE_PURCHASE: ["compro", "compra de", "en compra", "se compra[n]?", "necesito", "necesito comprar", "busco",
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

main_regex = "({ps_rg})\s*\d*\s*({curr_rg}){final_word_boundary}(?:en\s*efectivo)?\s*(?:a|en)\s*(\d+[\.,]?\d+)\s*(?:({target_curr_rg}){final_word_boundary})?"


def get_currencyad_from_ad(ad: Ad):

    regex = main_regex.format(
        ps_rg="|".join([action for sublist in action_regexes.values() for action in sublist]),
        curr_rg="|".join(list(itertools.chain.from_iterable(currencies_regexes.values()))),
        target_curr_rg="|".join(list(itertools.chain.from_iterable(currencies_regexes.values()))),
        final_word_boundary='\\b'
    )

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
    for currency_iso, regexes in currencies_regexes.items():
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

    price = None
    if matches.group(3):
        price = float(matches.group(3).replace(",", "."))
    else:
        # if we can't find a price then we have to ignore the ad
        return None

    # finding the target currency iso
    target_currency_iso = Ad.CUBAN_PESO_ISO

    # we only look in the title match due to the enormous amount of human errors in the currency_iso field, if there is
    # no currency there, we maintain the default value
    if matches.group(4):
        for currency_iso, regexes in currencies_regexes.items():
            if re.match("^({})$".format("|".join(regexes)), matches.group(4), re.IGNORECASE):
                target_currency_iso = currency_iso
                break

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

    print(matches.groups())
    print((action, source_currency_iso, price, target_currency_iso))

    return CurrencyAd(
        ad=ad,
        type=action,
        source_currency_iso=source_currency_iso,
        target_currency_iso=target_currency_iso,
        price=price
    )
