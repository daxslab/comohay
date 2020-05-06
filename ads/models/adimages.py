from django.db import models

from ads.models.ad import Ad


def get_image_filename(instance, filename):
    id = instance.ad.id
    return "uploads/ad_images/%s" % (id)

class AdImage(models.Model):
    ad = models.ForeignKey(Ad, default=None, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to=get_image_filename, verbose_name='Image')
    image = models.ImageField()

