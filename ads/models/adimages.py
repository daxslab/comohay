from django.db import models
from django.db.models.signals import post_init, post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from ads.models.ad import Ad


class AdImage(models.Model):
    ad = models.ForeignKey(Ad, default=None, on_delete=models.CASCADE, verbose_name=_('Ad'))
    image = models.ImageField(verbose_name=_('Image'))

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')


@receiver(post_init, sender=AdImage)
def backup_image_path(sender, instance, **kwargs):
    if (instance.id is not None):
        instance._current_image_file = instance.image


@receiver(post_save, sender=AdImage)
def delete_old_image(sender, instance, **kwargs):
    if hasattr(instance, '_current_image_file'):
        if instance._current_image_file.path != instance.image.path:
            instance._current_image_file.delete(save=False)


@receiver(pre_delete, sender=AdImage)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)
