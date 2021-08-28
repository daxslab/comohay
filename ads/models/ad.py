import sys
from decimal import Decimal
from encodings.base64_codec import base64_encode

from autoslug import AutoSlugField
from django import urls
from django.db import models
from django.http import QueryDict
from django_currentuser.db.models import CurrentUserField
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from ads.models.basemodel import BaseModel
from ads.models.municipality import Municipality
from ads.models.province import Province


class Ad(BaseModel):
    CUBAN_PESO_ISO = 'CUP'
    CONVERTIBLE_CUBAN_PESO_ISO = 'CUC'
    MLC_ISO = 'MLC'
    AMERICAN_DOLLAR_ISO = 'USD'
    EURO_ISO = 'EUR'
    CANADIAN_DOLLAR_ISO = 'CAD'
    MEXICAN_PESO_ISO = 'MXN'
    ALLOWED_CURRENCIES = (
        (CUBAN_PESO_ISO, CUBAN_PESO_ISO),
        (MLC_ISO, MLC_ISO),
        (AMERICAN_DOLLAR_ISO, AMERICAN_DOLLAR_ISO),
        (EURO_ISO, EURO_ISO),
        (CANADIAN_DOLLAR_ISO, CANADIAN_DOLLAR_ISO),
        (MEXICAN_PESO_ISO, MEXICAN_PESO_ISO),
        (CONVERTIBLE_CUBAN_PESO_ISO, CONVERTIBLE_CUBAN_PESO_ISO),
    )

    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = AutoSlugField(populate_from='title', always_update=False, unique=False, verbose_name=_('Slug'))
    category = models.ForeignKey('categories.Category', null=True, on_delete=models.SET_NULL, verbose_name=_('Category'))
    description = models.TextField(verbose_name=_('Description'))
    price = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True, default=0.00, verbose_name=_('Price'))
    currency_iso = models.CharField(null=True, max_length=3, choices=ALLOWED_CURRENCIES, default='CUP', verbose_name=_('Currency'))
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Province'))
    municipality = models.ForeignKey(Municipality, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Municipality'))
    contact_phone = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Contact phone"))
    contact_email = models.EmailField(null=True, blank=True, verbose_name=_("Contact email"))
    external_source = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('External source'))
    external_id = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('External ID'))
    external_url = models.URLField(blank=True, null=True, verbose_name=_('External URL'))
    external_contact_id = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('External contact ID'))
    external_created_at = models.DateTimeField(blank=True, null=True, verbose_name=_('External created at'))
    created_by = CurrentUserField(verbose_name=_('Created by'))
    updated_by = CurrentUserField(on_update=True, related_name='%(class)s_updated_by', verbose_name=_('Updated by'))
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Ad')
        verbose_name_plural = _('Ads')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.external_source and self.external_url:
            return self.external_url
        return urls.reverse('ads:detail', args=(self.slug,))

    def get_url_with_redirection(self, absolute=True, request=None):
        scheme = request.get_scheme() if request else settings.SERVER_SCHEME
        hostname = request.get_host() if request else settings.SERVER_HOSTNAME
        query = QueryDict(mutable=True)
        ref = "{}://{}/".format(scheme, hostname)
        query['url'] = self.get_absolute_url()
        query['ref'] = base64_encode(bytes(ref, 'UTF-8'))[0].decode()
        query['ad'] = base64_encode(bytes(str(self.id), 'UTF-8'))[0].decode()
        url = urls.reverse('ads:to_external_url') + '?' + query.urlencode()
        return url if not absolute else "{}://{}{}".format(scheme, hostname, url)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.price is None:
            self.price = 0

        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False, soft=True):
        if soft:
            self.is_deleted = True
            self.save()
            return 0, {}

        return super().delete(using, keep_parents)

