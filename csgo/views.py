from django.views import View
from django.http.response import HttpResponse, HttpResponseNotModified
from django.views.generic.base import ContextMixin, TemplateView 
from django.views.generic import (CreateView,DetailView,DeleteView,UpdateView,ListView)

from django.urls import reverse
from django.shortcuts import redirect, render
from django.forms.formsets import formset_factory

from . import forms
from .models import Cart, CartItem, Listing,InventoryItem
from .filters import ListingFilter

class Index(TemplateView):
    template_name = 'base/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listing_latest'] = Listing.objects.filter(inventory__item_state=InventoryItem.LIS).select_related('inventory','inventory__item')  #TODO: Convert to manager
        return context
    
class ListingTradeView(TemplateView):
    template_name = 'csgo/listing_trade.html'
    purpose = 'TRADE'

    def get_queryset(self):
        return Listing.objects.select_related('inventory','inventory__item').filter(purpose=self.purpose,inventory__item_state=InventoryItem.LIS)

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['filter'] = ListingFilter(self.request.GET,self.get_queryset())
        return context
    
    def post(self,request,*args, **kwargs):
        items = request.POST.get('items')
        items = Listing.objects.filter(pk__in=items)
        return HttpResponseNotModified(items)

class ListingShopView(TemplateView):
    template_name = 'csgo/listing_shop.html'
    purpose = 'SELL'

    def get_queryset(self):
        return Listing.objects.select_related('inventory','inventory__item').filter(purpose=self.purpose,inventory__item_state=InventoryItem.LIS)

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['filter'] = ListingFilter(self.request.GET,self.get_queryset())
        return context
    
    def post(self,request,*args, **kwargs):
        items = request.POST.get('items')
        items = Listing.objects.filter(pk__in=items)
        return HttpResponseNotModified(items)

class ListingAuctionView(TemplateView):
    template_name = 'csgo/listing_auction.html'
    purpose = 'AUCTION'

    def get_queryset(self):
        return Listing.objects.select_related('inventory','inventory__item').filter(purpose=self.purpose,inventory__item_state=InventoryItem.LIS)

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['filter'] = ListingFilter(self.request.GET,self.get_queryset())
        return context
    
    def post(self,request,*args, **kwargs):
        items = request.POST.get('items')
        items = Listing.objects.filter(pk__in=items)
        return HttpResponseNotModified(items)

class ListingDetailView(DetailView):
    queryset = Listing.objects.select_related('owner','inventory','inventory__item').prefetch_related('inventory__addons')
    context_object_name = 'listing'
    fields = ('owner','item','float','price','tradable','inspect_url','date_created','addons')

    def post(self,request,*args, **kwargs):
        item = request.POST.get('item')
        try:
            item = int(item)
        except:
            return HttpResponse('NOT gud')
        cart = Cart.objects.get(owner=self.request.user)
        item_obj = Listing.objects.get(pk=item)
        cart.item.add(item_obj)
        cart.save()
        return render(request,'base/test.html',context={'ad':cart.item.all()})

class ListingDeleteView(DeleteView):
    model = Listing
    context_object_name = 'listing'
    success_url = '/'

class CartView(TemplateView):
    template_name = 'csgo/cart.html'
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        cart = Cart.objects.get(owner=self.request.user)
        context['buy'] = CartItem.objects.filter(cart=cart)
        return context

class InventoryListView(TemplateView):
    template_name = 'csgo/inventory_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inventory"] = InventoryItem.objects.filter(owner=self.request.user,item_state=InventoryItem.INV).select_related('item').prefetch_related('addons')
        context["listed"] = InventoryItem.objects.filter(owner=self.request.user,item_state=InventoryItem.LIS).select_related('item').prefetch_related('addons')
        context["transaction"] = InventoryItem.objects.filter(owner=self.request.user,item_state=InventoryItem.TRA).select_related('item').prefetch_related('addons')
        context["sold"] = InventoryItem.objects.filter(owner=self.request.user,item_state=InventoryItem.SOL).select_related('item').prefetch_related('addons')
        context["inventory_url"] = reverse('csgo:inventory')
        self.request.session.pop('to_list',None)
        return context
    
    def post(self,request):
        data = request.POST   
        items = data.getlist('item[]')                              # Get marked inventory items to create listing
        request.session['to_list'] = items
        return HttpResponse(reverse('csgo:inventory_create'))

class CheckoutView(TemplateView):
    template_name = 'csgo/checkout.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        cart = Cart.objects.get(owner=self.request.user)
        context['item'] = CartItem.objects.get(cart=cart,pk=self.kwargs.get('pk'))
        return context

class InventoryCreateView(CreateView):
    template_name = 'base/base/test.html'
    form_class = forms.InventoryCreateForm
    
    def get(self,request,*args, **kwargs):
        items = request.session.get('to_list',None)
        if not items:
            return redirect('csgo:inventory')
        query = InventoryItem.objects.filter(owner=request.user,assetid__in=items).prefetch_related('addons').select_related('owner','item')
        initial=[{
                        'owner':item.owner,
                        'inventory':item,
                        'item_name':item.item.market_hash_name,
                        'item_image':item.item.get_icon_small(),}
                        for item in query]
        form = formset_factory(self.form_class,extra=0)
        form = form(initial=initial)
            
        ctx = {'form':form}
        return render(request,'base/test.html',ctx)

    def post(self,request,*args, **kwargs):
        items = request.session.get('to_list',None)
        if not items:
            return redirect('csgo:inventory')
        query = InventoryItem.objects.filter(owner=request.user,assetid__in=items).prefetch_related('addons').select_related('owner','item')
        initial=[{
                        'owner':item.owner,
                        'inventory':item,
                        'item_name':item.item.market_hash_name,
                        'item_image':item.item.get_icon_small(),
                        } for item in query]
        form = formset_factory(self.form_class)
        form = form(request.POST,initial=initial)

        if form.is_valid():
            for f in form:
                if len(f.changed_data) > 2:
                    return HttpResponse(f.changed_data)
                instance = f.save(commit=False)
                instance.owner = request.user
                instance.inventory.item_state = InventoryItem.LIS
                instance.inventory.save(update_fields=['item_state'])
                instance.save()

            request.session.pop('to_list',None)
            return HttpResponse('createdlisting')
        ctx = {'form':form}
        return render(request,'base/test.html',ctx)
    




def test2(request,*args, **kwargs):
    InventoryItem.update_inventory(request.user)
    return render(request,'base/test.html')