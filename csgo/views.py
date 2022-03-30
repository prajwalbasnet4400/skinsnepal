from django.db.models.aggregates import Min
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.views import View
from django.http.response import JsonResponse
from django.views.generic.base import TemplateView
from django.views.generic import DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator


from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .logic.steam_inventory import InventoryItemLogic
from .logic.parsers import get_item_price
from .forms import InventoryCreateForm
from chat.models import Room, Message

from . import models
from . import filters
from . import mixins


class IndexView(TemplateView):
    template_name = 'csgo/index.html'


class ListingBuyView(TemplateView):
    template_name = 'csgo/listing/listing_shop.html'
    paginate_by = 30
    queryset = models.Listing.objects.select_related('inventory', 'inventory__item').prefetch_related('inventory__addons','inventory__addons__item').filter(
        purpose="SELL", inventory__item_state=models.InventoryItem.ItemStateChoices.LIS).order_by('date_listed')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_no = self.request.GET.get('page')
        filtered = filters.ListingFilter(self.request.GET, self.queryset)
        filtered.page_obj = Paginator(
            filtered.qs, self.paginate_by).get_page(page_no)
        context['filter'] = filtered
        return context

class ListingDetailView(DetailView):
    template_name = 'csgo/listing/listing_detail.html'
    queryset = models.Listing.objects.select_related(
        'owner', 'inventory', 'inventory__item').prefetch_related('inventory__addons')
    context_object_name = 'listing'
    fields = ('owner', 'item', 'float', 'price', 'tradable',
              'inspect_url', 'date_created', 'addons')

    # Add to Cart
    def post(self, request, *args, **kwargs):
        listing = self.get_object()
        owner = request.user
        obj, created = models.CartItem.objects.get_or_create(
            owner=owner,
            listing=listing)
        if created:
            messages.success(request, 'Added to cart', 'Notify')
        else:
            messages.warning(request, 'Already in cart', 'Report')
        return redirect(listing)

class InventoryListView(LoginRequiredMixin, TemplateView):
    template_name = 'csgo/listing/inventory_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inventory"] = models.InventoryItem.objects.filter(
            owner=self.request.user, item_state=models.InventoryItem.ItemStateChoices.INV).select_related('item').prefetch_related('addons',"addons__item")
        return context

class ListingCreateView(mixins.IsOwnerMixin, View):
    template_name = 'csgo/listing/listing_create.html'
    form_class = InventoryCreateForm
    model = models.InventoryItem

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        if pk:
            obj = get_object_or_404(self.model, pk=pk)
        else:
            raise Http404
        return obj

    def is_object_owner(self, user, obj):
        return user == obj.owner

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        obj = self.get_object()
        ctx = {'form': form, 'obj': obj}
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
            form.add_error(field=None, error='Item doesn\'t belong to you')
        ctx = {'form': form, 'obj': inventory}
        return render(request, self.template_name, ctx)

class ListingDeleteView(mixins.IsOwnerMixin, DeleteView):
    model = models.Listing
    context_object_name = 'listing'
    success_url = '/'
    template_name = 'csgo/listing/listing_confirm_delete.html'

    def get_object(self, *args, **kwargs):
        return super().get_object(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'csgo/transaction/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buy'] = models.CartItem.objects.filter(owner=self.request.user).select_related('listing','listing__owner', 'listing__inventory', 'listing__inventory__item')\
            .prefetch_related('listing__inventory__addons')
        return context

class CartDeleteView(mixins.IsOwnerMixin, View):
    model = models.CartItem

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        if not pk:
            raise Http404
        obj = get_object_or_404(self.model, pk=pk)
        return obj

    def post(self, request, *args, **kwargs):
        cartitem = self.get_object()
        cartitem.delete()
        messages.success(request, 'Deleted From Cart', 'Notify')
        return redirect('csgo:cart')

class InventoryUpdateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        user = request.user
        inv = InventoryItemLogic(user)
        inv.update_inventory()
        messages.success(request, 'Inventory Updated', 'Notify')
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


class ChatOfferView(LoginRequiredMixin, View):
    model = models.Listing

    def post(self, request, *args, **kwargs):
        user = request.user
        listing = self.get_object()
        room = self.get_room(listing)
        Message.objects.create(
            room=room,
            user=user,
            username=user.username,
            content=self.get_message_content(listing),
        )
        return redirect(f"{reverse('chat:index')}?u={listing.owner.steamid64}")

    def get_object(self):
        pk = self.kwargs.get('pk')
        if not pk:
            raise Http404
        obj = get_object_or_404(self.model, pk=pk)
        if obj.owner == self.request.user:
            # Do something
            pass
        return obj

    def get_room(self, listing):
        user = self.request.user
        room = Room.objects.filter(user=user).filter(user=listing.owner)
        if room.exists():
            room = room.first()
        else:
            room = Room.objects.create()
            room.user.add(user)
            room.user.add(listing.owner)
        return room

    def get_message_content(self, listing):
        content = f'Hello, Im intrested in this item you listed.<a href="{listing.get_absolute_url()}">{listing.market_hash_name}</a>'
        return content

