from django.contrib import admin
from .models import Item, Listing,ListingAddon

admin.site.register(Item)
admin.site.register(Listing)
admin.site.register(ListingAddon)