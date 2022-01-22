from django.db.models.aggregates import Max, Min
from django.views import View
from django.http.response import HttpResponse, JsonResponse
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic import DetailView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
import json

from django.urls import reverse
from django.shortcuts import get_object_or_404

from csgo.api_parsers.steam_inventory import Inventory
from csgo.api_parsers.parsers import get_item_price

from . import serializers
from . import models
from . import filters
from .logic import khalti

class IndexView(TemplateView):
    template_name = 'base/index.html'
    csgo_queryset = models.Listing.objects.filter(inventory__item_state=models.InventoryItem.LIS).order_by(
                                                'date_listed').select_related('inventory','inventory__item')[:8]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listing_latest'] = self.csgo_queryset
        return context
    
class ListingBuyView(TemplateView):                                 # TODO: Pagination
    template_name = 'csgo/listing/listing_shop.html'
    paginate_by = 50
    queryset = models.Listing.objects.select_related('inventory','inventory__item').prefetch_related('inventory__addons').filter(
                                                                    purpose="SELL",inventory__item_state=models.InventoryItem.LIS)

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['filter'] = filters.ListingFilter(self.request.GET,self.queryset)
        return context
    

class ListingDetailView(DetailView):
    template_name = 'csgo/listing/listing_detail.html'
    queryset = models.Listing.objects.select_related('owner','inventory','inventory__item').prefetch_related('inventory__addons')
    context_object_name = 'listing'
    fields = ('owner','item','float','price','tradable','inspect_url','date_created','addons')

    def get_object(self):
        param = self.kwargs.get('uuid')
        obj = get_object_or_404(self.queryset,unique_id=param)
        return obj



class InventoryListView(LoginRequiredMixin,TemplateView):
    template_name = 'csgo/listing/inventory_list.html'

    def get(self,request,*args, **kwargs):
        response = super().get(request,*args, **kwargs)
        inv = Inventory(self.request.user)
        inv.update_inventory()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inventory"] = models.InventoryItem.objects.filter(
                            owner=self.request.user,item_state=models.InventoryItem.INV).select_related('item').prefetch_related('addons')
        return context
    
    def post(self,request):
        data = request.POST   
        items = data.get('item')
        request.session['to_list'] = items
        return HttpResponse(reverse('csgo:inventory_create'))

class ListingCreateView(LoginRequiredMixin,TemplateView):
    template_name = 'csgo/listing/listing_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['to_list_url'] = reverse('csgo:to_list')
        return context

    def post(self,request):
        items = json.loads(request.body)
        items = items['items']
        pks = [item['pk'] for item in items]
        invs = models.InventoryItem.objects.in_bulk(pks,field_name='pk')
        for item in items:
            price = item.get('price')*100
            obj = models.Listing(owner=request.user,inventory=invs[item.get('pk')],price=price)
            obj.save()
            obj.inventory.item_state = models.InventoryItem.LIS
            obj.inventory.save()
        request.session.pop('to_list')
        return HttpResponse('Success',status=200)

class InventoryToList(View):
    def get(self,request):
        items = request.session.get('to_list','')
        items = items.split(',')
        query = models.InventoryItem.objects.filter(owner=request.user,assetid__in=items).prefetch_related('addons').select_related('owner','item')
        serializer = serializers.InventoryItemSerializer(query,many=True)
        response = json.dumps(serializer.data)
        return HttpResponse(response)

class ListingDeleteView(LoginRequiredMixin,DeleteView):
    model = models.Listing
    context_object_name = 'listing'
    success_url = '/'
    template_name = 'csgo/listing/listing_confirm_delete.html'

class CartView(LoginRequiredMixin,TemplateView):
    template_name = 'csgo/transaction/cart.html'
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['buy'] = models.CartItem.objects.filter(cart__owner=self.request.user)
        return context
        
class CartAddView(View):
    def post(self,request,*args, **kwargs):
        item = request.POST.get('item')
        cart = models.Cart.objects.get(owner=request.user)
        item_obj = models.Listing.objects.filter(pk=item)
        
        if item_obj.exists():
            resp = {'success' : True,'message' : 'Added to cart'}
            cart.item.add(item_obj.first())
            cart.save()
        else:
            resp = {'success' : False,'message' : 'Listing does not exist'}

        return JsonResponse(resp)

class CartDeleteView(View):
    def post(self,request,*args, **kwargs):
        queryset = models.CartItem.objects.filter(cart__owner=request.user)
        id = request.POST.get('id')
        obj = get_object_or_404(queryset,pk=id)
        obj.delete()
        resp = {'success':True,'message':'Listing removed from cart'}
        return JsonResponse(resp)


class CheckOutView(View):
    def post(self,request,*args, **kwargs):                 # Checkout
        buyer = request.user
        item = request.POST.get('item')
        cart_item = models.CartItem.objects.get(cart__owner=request.user,pk=item)
        if buyer.credit < cart_item.listing.price:
            return HttpResponse('Insufficient funds',status=200)
        obj = models.Transaction(buyer=buyer,listing=cart_item.listing)
        obj.save()
        buyer.credit = buyer.subtract_credit(cart_item.listing.price)
        buyer.save()
        cart_item.delete()
        return HttpResponse(status=200)
        
class TransactionListView(LoginRequiredMixin,TemplateView):
    template_name = 'csgo/transaction/transaction_list.html'

    def get_context_data(self, **kwargs):
        queryset = models.Transaction.objects.filter(buyer=self.request.user).select_related('buyer','listing','listing__inventory').order_by('-state_last_changed')
        context = super().get_context_data(**kwargs)
        context['filter'] = filters.TransactionFilter(self.request.GET,queryset)        
        return context

class TransactionDetailView(LoginRequiredMixin,DetailView):
    model = models.Transaction
    template_name = 'csgo/transaction/transaction.html'
    context_object_name = 'transaction'

class WalletView(LoginRequiredMixin,ListView):
    model = models.WalletTransaction
    template_name = 'csgo/wallet/wallet_list.html'
    context_object_name = 'txns'

    def post(self,request,*args, **kwargs):
        user = self.request.user
        data = request.POST
        if data.get('type') == 'add_funds':
            payload = {"token": data.get('token'),"amount": data.get('amount')}
            resp = khalti.verify_khalti(payload)
            if resp.get('success'):
                resp_data = resp.get('data')
                klt = models.KhaltiTransaction(idx=data.get('idx'), amount=resp_data.get('amount'))
                klt.save()
                wlt_txn = models.WalletTransaction(user=user, amount=resp_data.get('amount'),type=models.WalletTransaction.TypeChoice.CR,khalti=klt)
                wlt_txn.save()
                user.credit = user.add_credit(resp_data.get('amount'))
                user.save()
            else:
                return HttpResponse(status=400)
        elif data.get('type') == 'withdraw_funds':
            pass
        else:
            return HttpResponse(status=400)
        return HttpResponse('DONE')
            


def get_item_price_view(request):
    names = set(request.GET.getlist('names'))
    response = {}
    steam = get_item_price(names)
    market = {}
    for name in names:
        q = models.Listing.objects.filter(inventory__item__market_hash_name__icontains=name).aggregate(Min('price'))
        market[name] = q['price__min']
    response['steam'] = steam
    response['market'] = market
    return JsonResponse(response)

def test(request,*args, **kwargs):
    return HttpResponse('DONE')