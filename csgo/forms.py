from django import forms

from . import models

class InventoryCreateForm(forms.ModelForm):
    item_image = forms.Field(widget=forms.HiddenInput(),disabled=True)
    item_name = forms.Field(widget=forms.HiddenInput(),disabled=True)

    immutable_fields = ('inventory',)

    class Meta:
        model = models.Listing
        fields = ('price','inventory')
        widgets = {
                    'tradable':forms.HiddenInput(),
                    'inventory':forms.HiddenInput()}

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.immutable_fields:
            self.fields[field].widget.attrs['readonly']='readonly'