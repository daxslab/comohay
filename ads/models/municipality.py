from django.db import models
from django.utils.translation import gettext_lazy as _

from ads.models.basemodel import BaseModel
from ads.models.province import Province


class Municipality(BaseModel):
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Province'))
    code = models.CharField(max_length=200, verbose_name=_('Code'))
    name = models.CharField(max_length=200, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Municipality')
        verbose_name_plural = _('Municipalities')

    def __str__(self):
        return self.name
