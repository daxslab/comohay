import datetime

from django.db.models import Model, DateTimeField

from ads.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserSearch(Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name=_('User'))
    search = models.TextField(verbose_name=_('Search'))
    autosuggestion = models.BooleanField(verbose_name=_('Autosuggestion'), default=False)
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('UserSearch')
        verbose_name_plural = _('UserSearches')
