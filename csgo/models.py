from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MinValueValidator,MaxValueValidator
from django.db.models.constraints import UniqueConstraint
from django.urls import reverse   
from django.db.models import Q
import datetime

from .parsers import get_csgo_items
from csgo.steam_inventory import Inventory
avatar_url = settings.STEAM_AVATAR_URL

class Item(models.Model):
    name = models.CharField(max_length=256)
    market_hash_name = models.CharField(unique=True,blank=False,null=False,max_length=255)

    icon_url = models.TextField(blank=True,null=True)
    icon_url_large = models.TextField(blank=True,null=True)
    
    type = models.CharField(max_length=64)
    sub_type = models.CharField(max_length=64,blank=True,null=True)
    weapon_type = models.CharField(max_length=64, blank=True,null=True)
    
    exterior = models.CharField(max_length=64, blank=True,null=True)
    rarity = models.CharField(max_length=64, blank=True,null=True)
    rarity_color = models.CharField(max_length=64, blank=True,null=True)
    
    stattrak = models.BooleanField(null=True)
    souvenir = models.BooleanField(null=True)
    tournament = models.CharField(max_length=255,blank=True,null=True)

    @staticmethod
    def get_update():
        items = get_csgo_items()
        obs = [Item(
            name=item.get('name'),
            market_hash_name=item.get('market_hash_name'),
            icon_url=item.get('icon_url'),
            icon_url_large=item.get('icon_url_large'),
            type=item.get('type'),
            sub_type=item.get('sub_type'),
            weapon_type=item.get('weapon_type'),
            exterior=item.get('exterior'),
            rarity=item.get('rarity'),
            rarity_color=item.get('rarity_color'),
            stattrak=item.get('stattrak'),
            souvenir=item.get('souvenir'),
            tournament=item.get('tournament'),
        ) for item in items]
        Item.objects.bulk_create(obs,ignore_conflicts=True)

    def get_icon(self):
        url = avatar_url
        if self.icon_url_large:
            icon = url+self.icon_url_large
        else:
            icon = url+self.icon_url
        return icon
    
    def get_icon_small(self):
        url = avatar_url
        icon = url+self.icon_url
        return icon

    def __str__(self):
        return self.market_hash_name
    

class Listing(models.Model):
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,null=False)
    item = models.ForeignKey(Item, models.CASCADE,null=False)
    inventory = models.OneToOneField('InventoryItem',on_delete=models.CASCADE,null=True)

    float = models.FloatField(validators=[MinValueValidator(0),MaxValueValidator(1)])
    price = models.PositiveBigIntegerField(validators=[MinValueValidator(1)],null=False,blank=False)
    tradable = models.BooleanField(default=True)

    date_created = models.DateTimeField(auto_now_add=True)
    addons = models.ManyToManyField(Item,related_name='addons',blank=True,through='ListingAddon')
    
    class Meta:
        ordering = ('-date_created',)
        constraints = [
            UniqueConstraint(fields=['owner','assetid'],name='unique_inventory_listing')
        ]

    def delete(self,*args, **kwargs):
        if self.inventory:
            self.inventory.is_listed = False
            self.inventory.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.item.market_hash_name
    
    def get_absolute_url(self):
        return reverse('csgo:detail', args=[str(self.id)])

class ListingAddon(models.Model):
    listing = models.ForeignKey(Listing,models.CASCADE)
    addon = models.ForeignKey(Item,models.CASCADE)

    def __str__(self):
        return self.addon.name


class InventoryAddon(models.Model):
    inventory = models.ForeignKey('InventoryItem',models.CASCADE)
    addon = models.ForeignKey(Item,models.CASCADE)

    def __str__(self):
        return f"{self.addon.name}"

class InventoryItem(models.Model):

    owner = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name='inventory') 
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='_inventory')

    classid = models.CharField(max_length=128)
    instanceid = models.CharField(max_length=128)
    assetid = models.CharField(max_length=128)

    float = models.FloatField(validators=[MinValueValidator(0),MaxValueValidator(1)],null=True)
    addons = models.ManyToManyField(Item,blank=True,through='InventoryAddon')
    tradable = models.BooleanField(default=True)
    inspect_url = models.TextField()

    is_listed = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('is_listed',)
        constraints = [models.UniqueConstraint(fields=['assetid','owner'],name='unique_item')]

    def __str__(self):
        return self.item.market_hash_name
    
    @staticmethod
    def rate_limited(owner):
        latest_obj = InventoryItem.objects.filter(owner=owner).latest('last_updated')
        current_time = datetime.datetime.now(datetime.timezone.utc)
        last_updated = current_time - latest_obj.last_updated
        print(last_updated)
        if last_updated.total_seconds() <= 60:
            return True
        else:
            return False

    @staticmethod
    def update_inventory(user):
        inv = Inventory(user.steamid())
        data = inv.get_data()
        objs = []
        assetids = []
        names = set()
        sticker_names = set()

        for item in data.values():
            assetids.append(item['assetid'])
            names.add(item['market_hash_name'])
            for sticker in item.get('stickers',[]):
                sticker_names.add(sticker)

        existing_items = {item.market_hash_name:item for item in Item.objects.filter(market_hash_name__in=names)}   # TODO:Convert it to in_bulk() method
        existing_inv = InventoryItem.objects.filter(assetid__in=assetids).values_list('assetid',flat=True)

        for item in data.values():
            if not item.get('market_hash_name') in existing_items.keys():
                continue
            if item.get('assetid') in existing_inv:
                continue
            float = Inventory.get_float_inplace(item['inspect_url'])
            inv =InventoryItem(
                owner=user,
                item=existing_items.get(item['market_hash_name']),
                classid=item['classid'],
                instanceid=item['instanceid'],
                assetid=item['assetid'],
                tradable=item['tradable'],
                inspect_url=item['inspect_url'],
                float=float)
            objs.append(inv)
        objs = InventoryItem.objects.bulk_create(objs)

        for obj in objs:                                # Stickers m2m field logic
            data_stickers = data[obj.assetid]
            for sticker in data_stickers.get('stickers',[]):
                if sticker not in sticker_names:
                    continue
                InventoryAddon.objects.create(
                    inventory=obj,
                    addon=Item.objects.filter(type='Sticker',market_hash_name__icontains=sticker).first()
                )
        InventoryItem.objects.exclude(owner=user,assetid__in=assetids).delete()