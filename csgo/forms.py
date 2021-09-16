from django import forms
from django.forms import fields
from django_select2 import forms as s2forms

from . import models

class ItemWidget(s2forms.ModelSelect2Widget):
    empty_label = "Select Item to create listing"
    search_fields = [
        "market_hash_name__icontains",
    ]
    attrs = {"style": "width: 100%"}

class AddonWidget(s2forms.ModelSelect2MultipleWidget):
    queryset = models.Item.objects.filter(type='Sticker')
    empty_label = "Select applied Stickers"
    search_fields = [
        "market_hash_name__icontains",
    ]

class ListingCreateForm(forms.ModelForm):
    float = forms.FloatField(max_value=1,min_value=0,widget=forms.NumberInput(attrs={'step':0.0000000001}))
    class Meta:
        model = models.Listing
        fields = ('item','float','price','addons')
        widgets = {
            "item":ItemWidget,
            "addons":AddonWidget,
        }
    attrs = {"style": "width: 100%"}


class ListingInventoryCreateForm(forms.ModelForm):
    item = forms.ChoiceField(disabled=True)
    class Meta:
        model = models.Listing
        fields = '__all__'

class InventoryForm(forms.Form):
    assetid = forms.CharField()
    classid = forms.CharField()
    instanceid = forms.CharField()
    market_hash_name = forms.CharField()
    stickers = forms.CharField()
    icon_url = forms.CharField()

