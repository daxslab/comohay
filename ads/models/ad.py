from django import urls
from django.db import models
from django_extensions.db.fields import AutoSlugField

from ads.models.municipality import Municipality
from ads.models.province import Province


class Ad(models.Model):
    title = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from=['title'])
    category = models.ForeignKey('categories.Category', null=True, on_delete=models.SET_NULL)
    description = models.TextField()
    price = models.DecimalField(max_digits=1000000, decimal_places=2, blank=True, null=True, default=0.00)
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.SET_NULL)
    municipality = models.ForeignKey(Municipality, blank=True, null=True, on_delete=models.SET_NULL)
    external_source = models.CharField(max_length=200, blank=True, null=True)
    external_id = models.CharField(max_length=200, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.external_source and self.external_url:
            return self.external_url
        return urls.reverse('ads:detail', args=(self.slug,))
