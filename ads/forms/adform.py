from categories.models import Category
from django.forms import ModelForm
from django_filters.fields import ModelChoiceField

from ads.models.ad import Ad


class AdForm(ModelForm):

    category = ModelChoiceField(Category.objects.exclude(parent=None).all())

    class Meta:
        model = Ad
        exclude = [
            'slug',
            'external_source',
            'external_id',
            'external_url',
            'created_at',
            'updated_at',
            'created_by',
            'created_at',
        ]
