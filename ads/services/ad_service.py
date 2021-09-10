from django.core.exceptions import EmptyResultSet
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


def has_duplicates(ad, verbose=False, title_mm=None, description_mm=None):
    """
    Returns true if the passed ad has a duplicate in the database using the solr index, otherwise returns false

    Arguments
        ad (`Ad`):
            The ad from whom to detect if it has a duplicate
        verbose (`string`):
            Whether to print or no information about the process
        title_mm (`string`):
            minimum should match for the ad title,see https://solr.apache.org/guide/6_6/the-dismax-query-parser.html#TheDisMaxQueryParser-Themm_MinimumShouldMatch_Parameter
        description_mm (`string`):
            minimum should match for the ad description, see https://solr.apache.org/guide/6_6/the-dismax-query-parser.html#TheDisMaxQueryParser-Themm_MinimumShouldMatch_Parameter
    """

    sqs = SearchQuerySet()

    if title_mm is None:
        title_mm = '{}<{}%'.format(settings.TITLE_MIN_WORDS, settings.TITLE_SIMILARITY)

    if description_mm is None:
        description_mm = '{}<{}%'.format(settings.DESCRIPTION_MIN_WORDS, settings.DESCRIPTION_SIMILARITY)

    clean_desc = double_clean(ad.description, sqs.query.backend)
    clean_desc = clean_desc.replace("'", "\\'")
    max_desc_len = len(ad.description) + int(len(ad.description) * settings.DESCRIPTION_LENGTH_DIFF)

    clean_title = double_clean(ad.title, sqs.query.backend)
    clean_title = clean_title.replace("'", "\\'")
    max_title_len = len(ad.title) + int(len(ad.title) * settings.TITLE_LENGTH_DIFF)

    ids_values = sqs.filter(
        content=Raw(
            "description_length:[0 TO {}] AND {{!dismax qf=description mm={} v='{}'}} AND title_length:[0 TO {}] AND {{!dismax qf=title mm={} v='{}'}}".format(
                max_desc_len, title_mm, clean_desc, max_title_len, description_mm, clean_title))
    ).values_list('id')

    ids = list(map(lambda x: x[0].split('.')[-1], ids_values))

    # TODO: think about adding a date comparison. It can be possible that the ad content is similar but corresponds
    #  to other intent of selling another stock of the same product

    a = Q(id__in=ids)
    b = Q()

    has_contact_info = False

    if ad.contact_phone:
        b |= Q(contact_phone=ad.contact_phone)
        has_contact_info = True

    if ad.contact_email:
        b |= Q(contact_email=ad.contact_email)
        has_contact_info = True

    if ad.external_contact_id and ad.external_source:
        b |= (Q(external_contact_id=ad.external_contact_id) & Q(external_source=ad.external_source))
        has_contact_info = True

    if ad.contact_tg:
        b |= Q(contact_tg=ad.contact_tg)
        has_contact_info = True

    if has_contact_info:
        # Looking for duplicated ads from the same contact
        duplicates = Ad.objects.filter(a & (b))
    else:
        # Looking for duplicate ads from the same source that don't have contact information
        duplicates = Ad.objects.filter(
            Q(id__in=ids) & Q(external_source=ad.external_source) & Q(contact_phone=None) & Q(contact_email=None) & Q(
                external_contact_id=None) & Q(contact_tg=None))

    if duplicates.count() > 0:
        if verbose:
            print('Found {} duplicates ({}) of ad:"{}"'.format(duplicates.count(), ','.join(ids), ad.title))
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
