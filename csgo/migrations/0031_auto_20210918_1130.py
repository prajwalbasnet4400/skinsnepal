# Generated by Django 3.1 on 2021-09-18 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csgo', '0030_auto_20210918_1124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='inspect_url',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
