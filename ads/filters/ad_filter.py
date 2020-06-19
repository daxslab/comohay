from django.utils.translation import gettext as _

from django.forms import TextInput
from django_filters import FilterSet, CharFilter

from ads.models import Ad
from django.db.models import Q


class AdFilter(FilterSet):
    title = CharFilter(method='filter_by_title_and_description', widget=TextInput(attrs={'placeholder': _("Search")}))

    class Meta:
        model = Ad
        fields = ['title']

    def filter_by_title_and_description(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))
