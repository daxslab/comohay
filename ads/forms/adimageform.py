from django.forms import ModelForm, ImageField, FileInput
from django.utils.translation import gettext_lazy as _
from ads.models.adimages import AdImage


class AdImageForm(ModelForm):

    image = ImageField(label=_('Image'))

    class Meta:
        model = AdImage
        fields = ('image',)
