from django.db import models
from django.utils.translation import gettext_lazy as _

from ads.models.basemodel import BaseModel
from comohay import settings


class Province(BaseModel):
    code = models.CharField(max_length=200, verbose_name=_('Code'))
    name = models.CharField(max_length=200, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Province')
        verbose_name_plural = _('Provinces')

    def display_name(self):
        if self.name in settings.PROVINCES_DISPLAY_NAMES_MAP:
            return settings.PROVINCES_DISPLAY_NAMES_MAP[self.name]
        return self.name

    def __str__(self):
        return self.name
