# Generated by Django 3.1 on 2021-09-10 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csgo', '0017_listingaddon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='addons',
        ),
        migrations.AddField(
            model_name='listing',
            name='addons',
            field=models.ManyToManyField(blank=True, related_name='addons', through='csgo.ListingAddon', to='csgo.Item'),
        ),
    ]
