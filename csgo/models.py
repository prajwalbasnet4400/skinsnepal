from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MinValueValidator,MaxValueValidator
from django.urls import reverse   

from .api_parsers.parsers import get_csgo_items

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
        return len(Item.objects.bulk_create(obs,ignore_conflicts=True))

    def get_icon(self):
        url = avatar_url
        if self.icon_url_large:
            icon = url+self.icon_url_large
        else:
            icon = url+self.icon_url
        return icon
    
    def get_sub_type(self):
        if self.sub_type:
            return self.sub_type
        else:
            return self.weapon_type

    def __str__(self):
        return self.market_hash_name
    

class Listing(models.Model):
    class PurposeChoices(models.TextChoices):
        TRA = "TRADE", "TRADE"
        SEL = "SELL", "SELL"
        AUC = "AUCTION", "AUCTION"

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,null=False)
    inventory = models.OneToOneField('InventoryItem',on_delete=models.CASCADE,null=True,related_name='listed')
    price = models.PositiveBigIntegerField(validators=[MinValueValidator(1)],null=False,blank=False)
    purpose = models.CharField(max_length=32,choices=PurposeChoices.choices,default=PurposeChoices.SEL)
    date_listed = models.DateTimeField(auto_now_add=True)

    def item(self):
        return self.inventory.item

    def get_price(self):
        return str(self.price)[:-2]
        
    def float(self):
        return str(self.inventory.float)[:8]

    def icon(self):
        return self.inventory.item.get_icon()
    
    def exterior(self):
        return self.inventory.item.exterior

    def rarity(self):
        return self.inventory.item.rarity

    def rarity_color(self):
        return self.inventory.item.rarity_color

    def stattrak(self):
        return self.inventory.item.stattrak

    def inspect_url(self):
        return self.inventory.inspect_url

    def name(self):
        return self.inventory.item.name

    def addons(self):
        return self.inventory.addons.all()

    def type(self):
        return self.inventory.item.get_sub_type()

    def get_steam_inv_url(self):
        return f"{self.owner.get_steam_url()}/inventory/#730_2_{self.inventory.assetid}"

    def save(self,*args, **kwargs):
        if not self.pk:
            inv = self.inventory
            inv.item_state=InventoryItem.ItemStateChoices.LIS
            inv.save()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('csgo:detail', args=[str(self.pk)])
    
    def __str__(self):
        return self.inventory.item.market_hash_name

class CartItem(models.Model):
    owner = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner','listing'],name='unique cartitem')]

    def __str__(self):
        return f"{self.owner.username}"
    
    def get_owner(self):
        return self.owner

class InventoryItem(models.Model):
    class ItemStateChoices(models.TextChoices):
        INV = "INVENTORY", "INVENTORY"
        LIS = "LISTED", "LISTED"
        TRA = "TRANSACTION", "LISTED"
        SOL = "SOLD", "LISTED"

    owner = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name='inventory') 
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='_inventory')
    classid = models.CharField(max_length=128)
    instanceid = models.CharField(max_length=128)
    assetid = models.CharField(max_length=128)
    paintindex = models.CharField(max_length=16,blank=False)
    paintseed = models.CharField(max_length=16,blank=False)
    defindex = models.CharField(max_length=16,blank=False)
    item_state = models.CharField(max_length=32,choices=ItemStateChoices.choices,default=ItemStateChoices.INV)
    inspect_url = models.TextField()
    float = models.FloatField(validators=[MinValueValidator(0),MaxValueValidator(1)],null=True)
    tradable = models.BooleanField(default=True)
    in_inventory = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['assetid','owner'],name='unique_item')]

    def get_addons(self):
        return self.addons.all()

    def get_float(self):
        return str(self.float)[:8]

    def icon(self):
        return self.item.get_icon()

    def market_hash_name(self):
        return self.item.market_hash_name
        
    def __str__(self):
        return self.assetid
    
    def get_steam_inv_url(self):
        return f"{self.owner.get_steam_url()}/inventory/#730_2_{self.assetid}"

    def get_owner(self):
        return self.owner

class Addon(models.Model):
    item = models.ForeignKey(Item,on_delete=models.PROTECT)
    inventory = models.ForeignKey(InventoryItem,on_delete=models.CASCADE,related_name='addons')

    def name(self):
        return self.item.name
    def icon(self):
        return self.item.get_icon()


class Transaction(models.Model): #TODO: Rewrite choices to use TextChoices class to clean this mess
    class StateChoices(models.TextChoices):
        PPD = "1", "PAYMENT PENDING"
        PCM = "2", "PAYMENT COMPLETE"
        TST = "3", "TRADE SENT"
        TAC = "4", "TRADE ACCEPTED"
        FTF = "5", "FUNDS TRANSFERRED"
        TCM = "6", "TRANSACTION COMPLETE"
        BYE = "100", "BUYER ERROR"
        SEE = "99", "SELLER ERROR"
    
    buyer = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    listing = models.OneToOneField(Listing,on_delete=models.PROTECT,related_name='transaction')
    state = models.CharField(max_length=64,choices=StateChoices.choices,default=StateChoices.PCM)
    
    trade_sent_screenshot = models.ImageField(upload_to='uploads')
    trade_recv_screenshot = models.ImageField(upload_to='uploads')

    state_last_changed = models.DateTimeField(auto_now=True)
    transaction_started = models.DateTimeField(auto_now_add=True)

    notification_sent = models.BooleanField(default=False)

    def save(self,*args, **kwargs):
        if not self.pk:
            inventory = self.listing.inventory
            inventory.item_state = InventoryItem.TRA
            inventory.save()
        self.notification_sent = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.buyer}-{self.pk}-{self.state}"

    def buyer_paid(self):                                               # Integrate with payment gateway
        return True
    
    def seller_paid(self):
        return True

class WalletTransaction(models.Model):
    class TypeChoice(models.TextChoices):
        CR = "CREDIT","CREDIT"
        DR = "DEBIT","DEBIT"

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    type = models.CharField(max_length=32,choices=TypeChoice.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    khalti = models.OneToOneField('KhaltiTransaction',on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f"{self.user}-{self.amount}-{self.type}"
    
    def get_amount(self):
        return self.amount//100

class KhaltiTransaction(models.Model):
    idx = models.CharField(max_length=128)
    amount = models.PositiveIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.idx
        
    def get_amount(self):
        return self.amount//100