from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MinValueValidator,MaxValueValidator
from django.db.models.constraints import UniqueConstraint
from django.urls import reverse   

from .parsers import get_csgo_items
from csgo.steam_inventory import Inventory

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
        ) for item in items if not Item.objects.filter(market_hash_name=item.get('market_hash_name')).exists()]
        Item.objects.bulk_create(obs,ignore_conflicts=False)

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

    classid = models.CharField(max_length=128,null=True,blank=True)
    instanceid = models.CharField(max_length=128,null=True,blank=True)
    assetid = models.CharField(max_length=128,null=True,blank=True)
    float = models.FloatField(validators=[MinValueValidator(0),MaxValueValidator(1)])
    price = models.PositiveBigIntegerField(null=False,blank=False)
    tradable = models.BooleanField(default=True)
    inspect_url = models.CharField(max_length=512,blank=True,null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    addons = models.ManyToManyField(Item,related_name='addons',blank=True,through='ListingAddon')
    
    class Meta:
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
    quantity = models.PositiveSmallIntegerField(default=1,validators=[MaxValueValidator(5)])

    def __str__(self):
        return self.addon.name

class InventoryItem(models.Model):
    owner = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name='inventory') 
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='_inventory')

    classid = models.CharField(max_length=128)
    instanceid = models.CharField(max_length=128)
    assetid = models.CharField(max_length=128)

    float = models.FloatField(validators=[MinValueValidator(0),MaxValueValidator(1)],null=True)
    addons = models.ManyToManyField(Item,blank=True)
    tradable = models.BooleanField(default=True)
    inspect_url = models.TextField()

    is_listed = models.BooleanField(default=False)


    class Meta:
        constraints = [models.UniqueConstraint(fields=['assetid','owner'],name='unique_item')]

    def __str__(self):
        return self.item.market_hash_name
    
    @staticmethod
    def update_inventory(user):
        inv = Inventory(user.steamid())
        data = inv.get_data()
        objs = []
        assetids = []
        for item in data.values():
            assetids.append(item['assetid'])
            if not Item.objects.filter(market_hash_name=item['market_hash_name']).exists():
                continue
            if InventoryItem.objects.filter(owner=user,assetid=item['assetid']).exists():
                continue
            float = Inventory.get_float_inplace(item['inspect_url'])
            inv =InventoryItem(
                owner=user,
                item=Item.objects.get(market_hash_name=item['market_hash_name']),
                classid=item['classid'],
                instanceid=item['instanceid'],
                assetid=item['assetid'],
                tradable=item['tradable'],
                inspect_url=item['inspect_url'],
                float=float)
            objs.append(inv)
        objs = InventoryItem.objects.bulk_create(objs)

        for obj in objs:
            stickers = [Item.objects.filter(market_hash_name__icontains=sticker).first() for sticker in data[obj.assetid].get('stickers',[])
                         if Item.objects.filter(market_hash_name__icontains=sticker).exists()]
            if len(stickers) == 0:
                continue 
            obj.addons.add(*stickers)
        InventoryItem.objects.exclude(owner=user,assetid__in=assetids).delete()