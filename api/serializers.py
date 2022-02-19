from rest_framework import serializers
from csgo.models import  Addon, CartItem, InventoryItem, Item, KhaltiTransaction, Listing, Transaction, WalletTransaction

class ItemSerializer(serializers.ModelSerializer):
    icon = serializers.URLField(source='get_icon')
    class Meta:
        model = Item
        fields = ['name', 'market_hash_name', 'icon', 'type', 'sub_type', 'weapon_type',
                  'exterior', 'rarity', 'rarity_color', 'stattrak', 'souvenir', 'tournament']

class AddonBaseSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    icon = serializers.URLField()
    class Meta:
        model = Addon
        fields = ['name','icon']

class InventoryItemListSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    addons = AddonBaseSerializer(source='get_addons',many=True)
    
    class Meta:
        model = InventoryItem
        fields = ['owner', 'item', 'classid', 'instanceid', 'assetid', 'paintindex', 'paintseed', 'float',
                  'defindex', 'addons', 'tradable', 'inspect_url', 'item_state', 'last_updated', 'in_inventory','id']

class InventoryItemResSerializer(InventoryItemListSerializer):
    class Meta:
        model = InventoryItem
        fields = ['owner', 'item', 'classid', 'instanceid', 'assetid', 'paintindex', 'paintseed', 'float',
                  'defindex', 'addons', 'tradable', 'inspect_url', 'item_state', 'last_updated', 'in_inventory']

class ListingListSerializer(serializers.ModelSerializer):
    inventory = InventoryItemResSerializer()
    class Meta:
        model = Listing
        fields = ['price','id','inventory']

class ListingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['price']

class ListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['inventory','price']

    def create(self, validated_data):
        if not validated_data.get('owner') == validated_data.get('inventory').owner:
            raise serializers.ValidationError('Item doesn\'t exists or doesnt belong to the user')
        return super().create(validated_data)

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id','listing']
        read_only_fields = ['id']

class CartItemListSerializer(serializers.ModelSerializer):
    listing = ListingListSerializer()
    class Meta:
        model = CartItem
        fields = ['listing','id']
        read_only_fields = ['id']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['buyer','listing','state','trade_sent_screenshot','trade_recv_screenshot','state_last_changed','transaction_started','notification_state']

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['user','amount','type','date_created','khalti']
        

class KhaltiTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhaltiTransaction
        fields = ['idx','amount','date_created']