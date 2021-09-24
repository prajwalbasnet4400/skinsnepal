from django.views import View
from django.http.response import HttpResponse
from django.views.generic.base import TemplateView 
from django.views.generic import (CreateView,DetailView,DeleteView,UpdateView,ListView)

from django.urls import reverse
from django.shortcuts import redirect, render
from django.forms.formsets import formset_factory
from django.views.generic.edit import FormView

from . import forms
from .models import Item, Listing,InventoryItem, ListingAddon
from .filters import ListingFilter

class Index(TemplateView):
    template_name = 'base/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listing_latest'] = Listing.objects.all().select_related('item').order_by('-date_created',)[:8]
        return context
    
class ListingListView(TemplateView):
    template_name = 'csgo/listing_list.html'
    queryset = Listing.objects.all().select_related('item')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['filter'] = ListingFilter(self.request.GET,self.queryset)
        return context

class ListingCreateView(CreateView):
    model = Listing
    context_object_name = 'listing'
    form_class = forms.ListingCreateForm
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ListingDetailView(DetailView):
    queryset = Listing.objects.select_related('owner','item').prefetch_related('addons')
    context_object_name = 'listing'
    fields = ('owner','item','float','price','tradable','inspect_url','date_created','addons')

class ListingDeleteView(DeleteView):
    model = Listing
    context_object_name = 'listing'
    success_url = '/'

class InventoryListView(TemplateView):
    template_name = 'csgo/inventory_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data"] = InventoryItem.objects.filter(owner=self.request.user).select_related('item').prefetch_related('addons')
        context["inventory_url"] = reverse('csgo:inventory')
        self.request.session.pop('to_list',None)
        return context
    
    def post(self,request):
        data = request.POST   
        items = data.getlist('item[]')                              # Get marked inventory items to create listing
        request.session['to_list'] = items
        return HttpResponse(reverse('csgo:inventory_create'))


class InventoryCreateView(CreateView):
    template_name = 'test.html'
    form_class = forms.InventoryCreateForm
    
    def get(self,request,*args, **kwargs):
        items = request.session.get('to_list',None)
        if not items:
            return redirect('csgo:inventory')
        query = InventoryItem.objects.filter(owner=request.user,assetid__in=items).prefetch_related('addons').select_related('owner','item')
        initial=[{
                        'owner':item.owner,
                        'item':item.item,
                        'inventory':item,
                        'classid':item.classid,
                        'instanceid':item.instanceid,
                        'assetid':item.assetid,
                        'tradable':item.tradable,
                        'inspect_url':item.inspect_url,
                        'item_name':item.item.market_hash_name,
                        'item_image':item.item.get_icon_small(),
                        'float':item.float,
                        'addons':[addon.id for addon in item.addons.all()]} for item in query]
        form = formset_factory(self.form_class,extra=0)
        form = form(initial=initial)
            
        ctx = {'form':form}
        return render(request,'test.html',ctx)

    def post(self,request,*args, **kwargs):
        items = request.session.get('to_list',None)
        if not items:
            return redirect('csgo:inventory')
        query = InventoryItem.objects.filter(owner=request.user,assetid__in=items).prefetch_related('addons').select_related('owner','item')
        initial=[{
                        'owner':item.owner,
                        'item':item.item,
                        'inventory':item,
                        'tradable':item.tradable,
                        'inspect_url':item.inspect_url,
                        'item_name':item.item.market_hash_name,
                        'item_image':item.item.get_icon_small(),
                        'float':item.float,
                        'addons':[addon.id for addon in item.addons.all()]} for item in query]
        form = formset_factory(self.form_class)
        form = form(request.POST,initial=initial)

        if form.is_valid():
            for f in form:
                if len(f.changed_data) != 1:
                    return HttpResponse(f.changed_data)
                instance = f.save(commit=False)
                instance.owner = request.user
                instance.inventory.is_listed = True
                instance.inventory.save(update_fields=['is_listed'])
                instance.save()

                objs = []
                for id in f['addons'].initial:
                    addon = ListingAddon(
                        listing=instance,
                        addon=Item.objects.get(pk=id)
                    )
                    objs.append(addon)
                ListingAddon.objects.bulk_create(objs)
            request.session.pop('to_list',None)
            return HttpResponse('createdlisting')
        ctx = {'form':form}
        return render(request,'base/test.html',ctx)
    




def test2(request,*args, **kwargs):
    if InventoryItem.rate_limited(request.user):
        return HttpResponse('Ratelimited')
    InventoryItem.update_inventory(request.user)
    return render(request,'test.html')