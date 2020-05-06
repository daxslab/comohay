from django.db import models

from ads.models.province import Province


class Municipality(models.Model):
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.CASCADE)
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
