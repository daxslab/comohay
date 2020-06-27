from django.db.models import Model

from ads.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserSearch(Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name=_('User'))
    search = models.TextField(verbose_name=_('Search'))
    daystamp = models.IntegerField(verbose_name=_('Daystamp'))

    class Meta:
        verbose_name = _('UserSearch')
        verbose_name_plural = _('UserSearches')
