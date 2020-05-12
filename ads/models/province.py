from django.db import models
from django.utils.translation import gettext_lazy as _

from ads.models.basemodel import BaseModel


class Province(BaseModel):
    code = models.CharField(max_length=200, verbose_name=_('Code'))
    name = models.CharField(max_length=200, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Province')
        verbose_name_plural = _('Provinces')

    def __str__(self):
        return self.name
