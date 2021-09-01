from django.db import models
from django.contrib.auth import get_user_model

class Item(models.Model):
    name = models.CharField(max_length=1024, blank=True, null=True)
    iconurl = models.CharField(max_length=5080, blank=True, null=True)
    type = models.CharField(max_length=128, blank=True, null=True)
    weapon_type = models.CharField(max_length=128, blank=True, null=True)
    gun_type = models.CharField(max_length=128, blank=True, null=True)
    exterior = models.CharField(max_length=128, blank=True, null=True)
    rarity = models.CharField(max_length=128, blank=True, null=True)
    rarity_color = models.CharField(max_length=128, blank=True, null=True)
    stattrak = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name

class Listing(models.Model):
    item = models.ForeignKey(Item, models.CASCADE)
    float = models.FloatField()
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    addons_test = models.ManyToManyField(Item,related_name='listings')
    def __str__(self):
        return self.item.name

class Addon(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name='addons')
    addon = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.addon.name