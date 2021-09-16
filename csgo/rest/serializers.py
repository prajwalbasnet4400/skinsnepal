from rest_framework import serializers
from csgo.models import Item,Listing


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['pk','name','iconurl']


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['pk','item','float','owner','price','date_created','addons']
        read_only_fields = ['date_created','owner']

class ListingNestedSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False,read_only=True)
    addons = ItemSerializer(many=True,read_only=True)
    class Meta:
        model = Listing
        fields = '__all__'