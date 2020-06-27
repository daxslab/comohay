from django.db.models import Model

from django.db import models
from django.utils.translation import gettext_lazy as _


class Search(Model):
    search = models.TextField(verbose_name=_('Search'))
    rank = models.FloatField(verbose_name=_('Rank'))

    class Meta:
        verbose_name = _('Search')
        verbose_name_plural = _('Searches')
