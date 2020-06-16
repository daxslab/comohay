from django import urls
from django.db import models
from django_currentuser.db.models import CurrentUserField
from django_extensions.db.fields import AutoSlugField
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from ads.models.basemodel import BaseModel
from ads.models.municipality import Municipality
from ads.models.province import Province


class Ad(BaseModel):
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = AutoSlugField(populate_from=['title'], verbose_name=_('Slug'))
    category = models.ForeignKey('categories.Category', null=True, on_delete=models.SET_NULL, verbose_name=_('Category'))
    description = models.TextField(verbose_name=_('Description'))
    price = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True, default=0.00, verbose_name=_('Price'))
    user_currency = models.CharField(null=True, max_length=3, choices=[('CUC', 'CUC'), ('CUP', 'CUP')], default='CUC', verbose_name=_('Currency'))
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Province'))
    municipality = models.ForeignKey(Municipality, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Municipality'))
    external_source = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('External source'))
    external_id = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('External ID'))
    external_url = models.URLField(blank=True, null=True, verbose_name=_('External URL'))
    created_by = CurrentUserField(verbose_name=_('Created by'))
    updated_by = CurrentUserField(on_update=True, related_name='%(class)s_updated_by', verbose_name=_('Updated by'))

    class Meta:
        verbose_name = _('Ad')
        verbose_name_plural = _('Ads')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.external_source and self.external_url:
            return self.external_url
        return urls.reverse('ads:detail', args=(self.slug,))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.user_currency == 'CUC':
            self.price = self.price * settings.CUC_TO_CUP_CHANGE

        super().save(force_insert, force_update, using, update_fields)

    def get_user_price(self):
        if self.user_currency == 'CUC':
            return self.price / settings.CUC_TO_CUP_CHANGE
        return self.price

