# Generated by Django 3.1 on 2021-09-16 11:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csgo', '0021_inventoryitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='float',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]