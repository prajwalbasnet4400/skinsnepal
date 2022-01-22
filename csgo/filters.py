import django_filters

from .models import Listing, Transaction

class ListingFilter(django_filters.FilterSet):
    
    class Meta:
        model = Listing
        fields = {
                    'price':['lte','gte'],
                    'inventory__item__market_hash_name':['icontains'],
                    }

class TransactionFilter(django_filters.FilterSet):
    
    class Meta:
        model = Transaction
        fields = {
                    'state':['exact'],
                    'listing__inventory__item__market_hash_name':['icontains']
                    }