from django.db import models
from django.utils.translation import gettext_lazy as _

from ads.models.ad import Ad


class AdImage(models.Model):
    ad = models.ForeignKey(Ad, default=None, on_delete=models.CASCADE, verbose_name=_('Ad'))
    image = models.ImageField(verbose_name=_('Image'))

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
