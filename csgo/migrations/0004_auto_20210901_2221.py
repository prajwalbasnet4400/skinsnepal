# Generated by Django 3.2.6 on 2021-09-01 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csgo', '0003_listing_addons_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='addons_test',
        ),
        migrations.AddField(
            model_name='listing',
            name='addons',
            field=models.ManyToManyField(related_name='addons', to='csgo.Item'),
        ),
        migrations.DeleteModel(
            name='Addon',
        ),
    ]