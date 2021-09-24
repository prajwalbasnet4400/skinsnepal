import django_filters

from .models import Listing

class ListingFilter(django_filters.FilterSet):
    
    class Meta:
        model = Listing
        fields = {
                    'price':['lt','gt'],
                    'tradable':['exact'],
                    'item__market_hash_name':['icontains']
                    }