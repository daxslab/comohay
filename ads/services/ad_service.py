from haystack.inputs import Raw

from haystack.query import SearchQuerySet
from django.db.models import Q

from ads.models import Ad
from comohay import settings

import logging


def double_clean(query_fragment, backend):
    """
    Provides a mechanism for sanitizing user input before presenting the
    value to the backend.

    A basic (override-able) implementation is provided.
    """
    if not isinstance(query_fragment, str):
        return query_fragment

    words = query_fragment.split()
    cleaned_words = []

    for word in words:
        if word in backend.RESERVED_WORDS:
            word = word.replace(word, word.lower())

        for char in backend.RESERVED_CHARACTERS:
            word = word.replace(char, "\\\\%s" % char)

        cleaned_words.append(word)

    return " ".join(cleaned_words)


def has_duplicates(ad, verbose=False):
    """
       Ad :param ad:
    """

    sqs = SearchQuerySet()
    similarity = int(settings.DESCRIPTION_SIMILARITY * 100)

    # If the query has less than 4 clauses then it has to match at 100%, otherwise the number computed in similarity
    similarity = '3<{}'.format(similarity)

    clean_desc = double_clean(ad.description, sqs.query.backend)
    clean_desc = clean_desc.replace("'", "\\'")
    max_desc_len = len(ad.description) + int(len(ad.description) * settings.DESCRIPTION_LENGTH_DIFF)

    clean_title = double_clean(ad.title, sqs.query.backend)
    clean_title = clean_title.replace("'", "\\'")
    max_title_len = len(ad.title) + int(len(ad.title) * settings.TITLE_LENGTH_DIFF)

    ids_values = sqs.filter(
        content=Raw(
            "description_length:[0 TO {}] AND {{!dismax qf=description mm={}% v='{}'}} AND title_length:[0 TO {}] AND {{!dismax qf=title mm={}% v='{}'}}".format(
                max_desc_len, similarity, clean_desc, max_title_len, similarity, clean_title))
    ).values_list('id')

    ids = list(map(lambda x: x[0].split('.')[-1], ids_values))

    if (ad.contact_phone is not None and ad.contact_phone != '') or (
            ad.contact_email is not None and ad.contact_email != '') or (
            ad.external_contact_id is not None and ad.external_contact_id != ''):
        # Looking for duplicated ads from the same contact
        a = Q(id__in=ids)
        b = Q(contact_email=ad.contact_email)
        c = Q(contact_phone=ad.contact_phone)
        d = Q(external_contact_id=ad.external_contact_id) & Q(external_source=ad.external_source)

        duplicates = Ad.objects.filter(a & (b | c | d)).exclude(
            external_source=ad.external_source,
            external_id=ad.external_id
        )

        if duplicates.count() > 0:
            if verbose:
                print('Found {} duplicates ({}) of ad:"{}"'.format(duplicates.count(), ','.join(ids), ad.title))
                for ad in duplicates.all():
                    print('Title: {}'.format(ad.title))
                print('------------------------------------------------------------------')
            return True

        return False

    else:
        # Looking for duplicate ads from the same source
        a = Q(id__in=ids)
        b = Q(external_source=ad.external_source)

        duplicates = Ad.objects.filter(a & b).exclude(
            external_source=ad.external_source,
            external_id=ad.external_id
        )

        if duplicates.count() > 0:
            if verbose:
                print('Removing {} duplicates ({}) of ad:"{}"'.format(duplicates.count(), ','.join(ids), ad.title))
                for ad in duplicates.all():
                    print('Title: {}'.format(ad.title))
                print('------------------------------------------------------------------')
            return True

        return False


def remove_duplicates(ad, verbose=False):
    """
    Ad :param ad:
    """

    sqs = SearchQuerySet()
    similarity = int(settings.DESCRIPTION_SIMILARITY * 100)

    # If the query has less than 4 clauses then it has to match at 100%, otherwise the number computed in similarity
    similarity = '3<{}'.format(similarity)

    clean_desc = double_clean(ad.description, sqs.query.backend)
    clean_desc = clean_desc.replace("'", "\\'")
    max_desc_len = len(ad.description) + int(len(ad.description) * settings.DESCRIPTION_LENGTH_DIFF)

    clean_title = double_clean(ad.title, sqs.query.backend)
    clean_title = clean_title.replace("'", "\\'")
    max_title_len = len(ad.title) + int(len(ad.title) * settings.TITLE_LENGTH_DIFF)

    ids_values = sqs.filter(
        content=Raw(
            "description_length:[0 TO {}] AND {{!dismax qf=description mm={}% v='{}'}} AND title_length:[0 TO {}] AND {{!dismax qf=title mm={}% v='{}'}}".format(
                max_desc_len, similarity, clean_desc, max_title_len, similarity, clean_title))
    ).values_list('id')

    ids = list(map(lambda x: x[0].split('.')[-1], ids_values))

    if (ad.contact_phone is not None and ad.contact_phone != '') or (
            ad.contact_email is not None and ad.contact_email != '') or (
            ad.external_contact_id is not None and ad.external_contact_id != ''):
        try:
            # Remove duplicated ads from same contact
            a = Q(id__in=ids)
            b = Q(contact_email=ad.contact_email)
            c = Q(contact_phone=ad.contact_phone)
            d = Q(external_contact_id=ad.external_contact_id) & Q(external_source=ad.external_source)

            to_delete = Ad.objects.filter(a & (b | c | d)).exclude(
                external_source=ad.external_source,
                external_id=ad.external_id
            )

            if verbose and to_delete.count() > 0:
                print('Removing {} duplicates ({}) of ad:"{}"'.format(to_delete.count(), ','.join(ids), ad.title))
                for ad in to_delete.all():
                    print('Title: {}'.format(ad.title))
                    # print('Description: {}'.format(ad.description))

                print('------------------------------------------------------------------')

            to_delete.delete()

        except Exception as e:
            logging.error("Error removing duplicated items: " + str(e))

    else:
        try:
            # Remove duplicated ads from same source
            a = Q(id__in=ids)
            b = Q(external_source=ad.external_source)

            to_delete = Ad.objects.filter(a & b).exclude(
                external_source=ad.external_source,
                external_id=ad.external_id
            )

            if verbose and to_delete.count() > 0:
                print('Removing {} duplicates ({}) of ad:"{}"'.format(to_delete.count(), ','.join(ids), ad.title))
                for ad in to_delete.all():
                    print('Title: {}'.format(ad.title))
                    # print('Description: {}'.format(ad.description))

                print('------------------------------------------------------------------')

            to_delete.delete()

        except Exception as e:
            logging.error("Error removing duplicated items: " + str(e))
