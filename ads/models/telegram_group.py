from django.db import models
from ads.models.basemodel import BaseModel
from ads.models.municipality import Municipality
from ads.models.province import Province
from django.utils.translation import gettext_lazy as _


class TelegramGroup(BaseModel):
    username = models.CharField(max_length=32, verbose_name="Username")
    link = models.URLField(verbose_name="Link")
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Province'))
    municipality = models.ForeignKey(Municipality, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Municipality'))
