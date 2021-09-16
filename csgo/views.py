from django.views import View
from django.views.generic import (CreateView,DetailView,DeleteView,UpdateView,ListView)
from django.shortcuts import render

from .models import Listing,InventoryItem
from . import forms
from .steam_inventory import Inventory

class Index(View):
    template_name = 'index.html'

    def get(self,request,*args, **kwargs):
        ctx ={}
        ctx['listing_latest'] = Listing.objects.select_related('item').all().order_by('-date_created',)[:8]
        return render(request,self.template_name,ctx)

class ListingListView(ListView):
    model = Listing
    queryset = Listing.objects.all().select_related('item')
    context_object_name = 'listing_list'

class ListingCreateView(CreateView):
    model = Listing
    context_object_name = 'listing'
    form_class = forms.ListingCreateForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.owner = self.request.user
        instance.save()
        return super().form_valid(form)

class ListingDetailView(DetailView):
    model = Listing
    context_object_name = 'listing'
    fields = '__all__'

class ListingDeleteView(DeleteView):
    model = Listing
    context_object_name = 'listing'
    success_url = '/'

class ListingUpdateView(UpdateView):
    model = Listing
    context_object_name = 'listing'

class InventoryView(ListView):
    template_name = 'csgo/inventory.html'
    context_object_name = 'items'
    model = InventoryItem