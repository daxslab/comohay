from django.forms import ModelForm, ImageField

from ads.models.adimages import AdImage


class AdImageForm(ModelForm):
    image = ImageField(label='Image', required=False)
    class Meta:
        model = AdImage
        fields = ('image', )
