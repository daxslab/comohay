from django.db.models import Model, DateTimeField
from django.utils.translation import gettext_lazy as _


class BaseModel(Model):
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    class Meta:
        abstract=True