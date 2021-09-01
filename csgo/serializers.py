from rest_framework import serializers
from .models import Item,Listing,Addon


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name','iconurl']


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['item','float','owner','price','date_created','addons']
        read_only_fields = ['date_created','addons','owner']




class AddonSerializer(serializers.ModelSerializer):
    addon = ItemSerializer(many=False,read_only=True)
    class Meta:
        model = Addon
        fields = ['addon']

class ListingList(serializers.ModelSerializer): #LIST 
    item = ItemSerializer(many=False,read_only=True)
    addons = AddonSerializer(many=True,read_only=True)
    class Meta:
        model = Listing
        fields = ['item','float','owner','price','date_created','addons']
        read_only_fields = ['owner']