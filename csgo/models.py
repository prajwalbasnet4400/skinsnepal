from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MinValueValidator,MaxValueValidator

from django.urls import reverse   

avatar_url = settings.STEAM_AVATAR_URL

class Item(models.Model):
    name = models.CharField(max_length=256)
    market_hash_name = models.CharField(unique=True,max_length=255)

    icon_url = models.TextField(blank=True)
    icon_url_large = models.TextField(null=True,blank=True)
    
    type = models.CharField(max_length=64)
    sub_type = models.CharField(max_length=64,null=True,blank=True)
    weapon_type = models.CharField(max_length=64,null=True, blank=True)
    
    exterior = models.CharField(max_length=64,null=True, blank=True)
    rarity = models.CharField(max_length=64,null=True, blank=True)
    rarity_color = models.CharField(max_length=64,null=True, blank=True)
    
    stattrak = models.BooleanField(null=True)
    souvenir = models.BooleanField(null=True)
    tournament = models.CharField(max_length=255,null=True,blank=True)


    def get_icon(self):
        url = avatar_url
        if self.icon_url_large:
            icon = url+self.icon_url_large
        else:
            icon = url+self.icon_url
        return icon

    def __str__(self):
        return self.market_hash_name
    

class Listing(models.Model):
    item = models.ForeignKey(Item, models.CASCADE)
    float = models.FloatField(validators=[MinValueValidator(0),MaxValueValidator(1)])
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    addons = models.ManyToManyField(Item,related_name='addons',blank=True)
    
    def __str__(self):
        return self.item.market_hash_name
    
    def get_absolute_url(self):
        return reverse('csgo:detail', args=[str(self.id)])