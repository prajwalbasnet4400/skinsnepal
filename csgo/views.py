from distutils.log import error
from django.db.models.aggregates import Max, Min
from django.forms import ValidationError
from django.views import View
from django.http.response import HttpResponse, JsonResponse
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render

from .api_parsers.steam_inventory import Inventory
from .api_parsers.parsers import get_item_price
from .forms import InventoryCreateForm

from . import models
from . import filters
from .logic import khalti
from . import auth_mixins

class IndexView(TemplateView):
    template_name = 'csgo/index.html'

class ListingBuyView(TemplateView):                                 # TODO: Pagination
    template_name = 'csgo/listing/listing_shop.html'
    paginate_by = 50
    queryset = models.Listing.objects.select_related('inventory', 'inventory__item').prefetch_related('inventory__addons').filter(
        purpose="SELL", inventory__item_state=models.InventoryItem.ItemStateChoices.LIS)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = filters.ListingFilter(
            self.request.GET, self.queryset)
        return context


class ListingDetailView(DetailView):
    template_name = 'csgo/listing/listing_detail.html'
    queryset = models.Listing.objects.select_related(
        'owner', 'inventory', 'inventory__item').prefetch_related('inventory__addons')
    context_object_name = 'listing'
    fields = ('owner', 'item', 'float', 'price', 'tradable',
              'inspect_url', 'date_created', 'addons')

    # Add to Cart
    def post(self,request,*args, **kwargs):
        listing = self.get_object()
        owner = request.user
        obj, created = models.CartItem.objects.get_or_create(
                                                    owner=owner,
                                                    listing=listing)
        if created:
            messages.success(request,'Added to cart','Notify')
        else:
            messages.warning(request,'Already in cart','Report')
        return redirect(listing)

class InventoryListView(LoginRequiredMixin, TemplateView):
    template_name = 'csgo/listing/inventory_list.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        inv = Inventory(self.request.user)
        inv.update_inventory()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inventory"] = models.InventoryItem.objects.filter(
            owner=self.request.user, item_state=models.InventoryItem.ItemStateChoices.INV).select_related('item').prefetch_related('addons')
        return context

    def post(self, request):
        data = request.POST
        items = data.get('item')
        request.session['to_list'] = items
        return HttpResponse(reverse('csgo:inventory_create'))


class ListingCreateView(auth_mixins.IsOwnerMixin,View):
    template_name = 'csgo/listing/listing_create.html'
    form_class = InventoryCreateForm
    model = models.InventoryItem

    def get_object(self, *args, **kwargs):
        if not hasattr(self,'obj'):
            obj = get_object_or_404(self.model, pk=self.kwargs.get('pk'))
            self.obj = obj
        return self.obj

    def is_object_owner(self, user, obj):
        return user == obj.owner

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        obj = self.get_object()
        ctx = {'form': form,'obj':obj}
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        inventory = self.get_object()

        if self.is_object_owner(request.user, self.get_object()):
            if form.is_valid():
                owner = request.user
                purpose = models.Listing.PurposeChoices.SEL
                price = form.cleaned_data.get('price') * 100
                listing, created = models.Listing.objects.get_or_create(
                    owner=owner,
                    inventory=inventory,
                    defaults={
                        'price': price,
                        'purpose': purpose
                    })
                if created:
                    messages.add_message(
                        request, messages.SUCCESS, f'Listing Created for {listing}', 'Notify')
                else:
                    messages.add_message(
                        request, messages.INFO, 'Listing already exists, Please delete old listing', 'Report')

                return redirect(listing)
        else:
            form.add_error(field=None,error='Item doesn\'t belong to you')
        ctx = {'form': form, 'obj': inventory}
        return render(request, self.template_name, ctx)

class ListingDeleteView(auth_mixins.IsOwnerMixin, DeleteView):
    model = models.Listing
    context_object_name = 'listing'
    success_url = '/'
    template_name = 'csgo/listing/listing_confirm_delete.html'


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'csgo/transaction/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buy'] = models.CartItem.objects.filter(owner=self.request.user).select_related('listing','listing__inventory','listing__inventory__item').prefetch_related('listing__inventory__addons')
        return context

class CartDeleteView(auth_mixins.IsOwnerMixin,View):
    def get_object(self, *args, **kwargs):
        obj = get_object_or_404(models.CartItem,pk=self.request.POST.get('cartitem')) 
        return obj

    def post(self,request,*args, **kwargs):
        cartitem = self.get_object()
        cartitem.delete()
        messages.success(request,'Deleted From Cart','Notify')
        return redirect('csgo:cart')

class CheckOutView(View):
    def post(self, request, *args, **kwargs):                 # Checkout
        buyer = request.user
        item = request.POST.get('item')
        cart_item = models.CartItem.objects.get(
            cart__owner=request.user, pk=item)
        if buyer.credit < cart_item.listing.price:
            return HttpResponse('Insufficient funds', status=200)
        obj = models.Transaction(buyer=buyer, listing=cart_item.listing)
        obj.save()
        buyer.credit = buyer.subtract_credit(cart_item.listing.price)
        buyer.save()
        cart_item.delete()
        return HttpResponse(status=200)


class TransactionListView(LoginRequiredMixin, TemplateView):
    template_name = 'csgo/transaction/transaction_list.html'

    def get_context_data(self, **kwargs):
        queryset = models.Transaction.objects.filter(buyer=self.request.user).select_related(
            'buyer', 'listing', 'listing__inventory').order_by('-state_last_changed')
        context = super().get_context_data(**kwargs)
        context['filter'] = filters.TransactionFilter(
            self.request.GET, queryset)
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = models.Transaction
    template_name = 'csgo/transaction/transaction.html'
    context_object_name = 'transaction'


class WalletView(LoginRequiredMixin, ListView):
    model = models.WalletTransaction
    template_name = 'csgo/wallet/wallet_list.html'
    context_object_name = 'txns'

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = request.POST
        if data.get('type') == 'add_funds':
            payload = {"token": data.get(
                'token'), "amount": data.get('amount')}
            resp = khalti.verify_khalti(payload)
            if resp.get('success'):
                resp_data = resp.get('data')
                klt = models.KhaltiTransaction(idx=data.get(
                    'idx'), amount=resp_data.get('amount'))
                klt.save()
                wlt_txn = models.WalletTransaction(user=user, amount=resp_data.get(
                    'amount'), type=models.WalletTransaction.TypeChoice.CR, khalti=klt)
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

class InventoryManageView(LoginRequiredMixin,View):

    def post(self,request,*args, **kwargs):
        user = request.user
        inv = Inventory(user)
        inv.update_inventory()
        messages.success(request,'Inventory Updated','Notify')
        return redirect('csgo:inventory')

def get_item_price_view(request):
    names = set(request.GET.getlist('names'))
    response = {}
    steam = get_item_price(names)
    market = {}
    for name in names:
        q = models.Listing.objects.filter(
            inventory__item__market_hash_name__icontains=name).aggregate(Min('price'))
        market[name] = q['price__min']
    response['steam'] = steam
    response['market'] = market
    return JsonResponse(response)


def test(request, *args, **kwargs):
    return HttpResponse('DONE')
