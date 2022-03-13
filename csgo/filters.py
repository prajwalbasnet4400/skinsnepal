from django_filters import rest_framework as filters

from .models import Listing, Transaction, InventoryItem
from django.forms.widgets import TextInput

class ListingFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='inventory__item__market_hash_name',
                                lookup_expr='icontains',label='Search',widget=TextInput(attrs={'placeholder':'MAC-10 | Propaganda (Battle-Scarred)'}))
    class Meta:
        model = Listing
        fields = ['name']

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
