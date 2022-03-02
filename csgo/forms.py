from django import forms

from . import models

class InventoryCreateForm(forms.ModelForm):
    class Meta:
        model = models.Listing
        fields = ('price',)