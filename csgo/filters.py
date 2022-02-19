from django_filters import rest_framework as filters

from .models import Listing, Transaction, InventoryItem


class ListingFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='inventory__item__market_hash_name',lookup_expr='icontains')
    class Meta:
        model = Listing
        fields = {
            'price': ['lte', 'gte'],
            'id':['exact','in']
        }

class InventoryItemFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='item__market_hash_name',lookup_expr='icontains')
    class Meta:
        model = InventoryItem
        fields = {
            'float':['lte']
        }


class TransactionFilter(filters.FilterSet):
    class Meta:
        model = Transaction
        fields = {
            'state': ['exact'],
            'listing__inventory__item__market_hash_name': ['icontains']
        }
