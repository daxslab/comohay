# Generated by Django 3.0.7 on 2021-08-29 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0025_ad_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='contact_tg',
            field=models.CharField(max_length=200, null=True, verbose_name='Contact telegram'),
        ),
    ]