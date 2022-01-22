from rest_framework import serializers
from .models import InventoryItem, Item

class AddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['market_hash_name','get_icon_small']

    def get_icon_small(self,instance):
        return instance.get_icon_small()

class InventoryItemSerializer(serializers.ModelSerializer):
    addons = AddonSerializer(many=True, read_only=True)
    class Meta:
        model = InventoryItem
        fields = [
            'pk',
            'paintseed','float',
            'inspect_url','icon',
            'market_hash_name','addons'
        ]

    def get_icon(self,instance):
        return instance.item.get_icon_small()

    def get_market_hash_name(self,instance):
        return instance.item.market_hash_name