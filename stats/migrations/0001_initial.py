# Generated by Django 3.0.7 on 2021-08-23 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_currency_iso', models.CharField(max_length=3)),
                ('target_currency_iso', models.CharField(max_length=3)),
                ('type', models.CharField(choices=[('buy', 'Buy price'), ('sell', 'Sell price'), ('mid', 'Mid price')], max_length=10)),
                ('wavg', models.DecimalField(decimal_places=8, max_digits=14)),
                ('max', models.DecimalField(decimal_places=8, max_digits=14)),
                ('min', models.DecimalField(decimal_places=8, max_digits=14)),
                ('ads_qty', models.IntegerField()),
                ('datetime', models.DateTimeField()),
            ],
        ),
    ]
