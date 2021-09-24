from django import forms
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

class InventoryCreateForm(forms.ModelForm):
    item_image = forms.Field(widget=forms.HiddenInput(),disabled=True)
    item_name = forms.Field(widget=forms.HiddenInput(),disabled=True)

    immutable_fields = ('item','tradable','inventory','float','addons')

    class Meta:
        model = models.Listing
        fields = ('item','tradable','price','float','inventory','addons')
        widgets = {
                    'item': forms.HiddenInput(),
                    'tradable':forms.HiddenInput(),
                    'assetid':forms.HiddenInput(),
                    'classid':forms.HiddenInput(),
                    'instanceid':forms.HiddenInput(),
                    'inventory':forms.HiddenInput(),
                    'addons':forms.MultipleHiddenInput(),
      
                    }

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.immutable_fields:
            self.fields[field].widget.attrs['readonly']='readonly'