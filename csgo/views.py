from django.forms.formsets import formset_factory
from django.http.response import HttpResponse
from django.views import View
from django.views.generic import (CreateView,DetailView,DeleteView,UpdateView,ListView)
from django.shortcuts import redirect, render
from django.urls import reverse 

from .models import Listing,InventoryItem
from . import forms

class Index(View):
    template_name = 'index.html'

    def get(self,request,*args, **kwargs):
        ctx ={}
        ctx['listing_latest'] = Listing.objects.all().select_related('item').order_by('-date_created',)[:8]
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
    queryset = Listing.objects.select_related('owner').prefetch_related('addons')
    context_object_name = 'listing'
    fields = '__all__'

class ListingDeleteView(DeleteView):
    model = Listing
    context_object_name = 'listing'
    success_url = '/'

class ListingUpdateView(UpdateView):
    model = Listing
    context_object_name = 'listing'

class InventoryView(View):
    template_name = 'csgo/inventory.html'
    context_object_name = 'inventory'
    model = InventoryItem

    def get(self,request):
        request.session.pop('to_list',None)
        # InventoryItem.update_inventory(request.user)
        query = InventoryItem.objects.filter(owner=self.request.user).select_related('item').prefetch_related('addons').order_by('is_listed')
        ctx = {'data':query,
                'inventory_url':reverse('csgo:inventory')}
        return render(request,self.template_name,ctx)
    
    def post(self,request):
        data = request.POST   
        items = data.getlist('item[]')
        request.session['to_list'] = items
        return HttpResponse(reverse('csgo:test'))

    
def test(request,*args, **kwargs):
    items = request.session.get('to_list',None)
    if not items:
        return redirect('csgo:inventory')
    query = InventoryItem.objects.filter(owner=request.user,assetid__in=items).prefetch_related('addons').select_related('owner')
    initial=[
                {
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
                    'addons':[addon.id for addon in item.addons.all()]
                } for item in query]
    if request.method == 'GET':
        form = formset_factory(forms.InventoryCreateForm,extra=0)
        form = form(initial=initial)
    else:                                                           #TODO:Addon m2m fields save
        form = formset_factory(forms.InventoryCreateForm)
        form = form(request.POST,initial=initial)
        if form.is_valid():
            for f in form:
                if len(f.changed_data) != 1:
                    return HttpResponse(f.changed_data)
                instance = f.save(commit=False)
                instance.owner = request.user
                instance.inventory.is_listed = True
                instance.inventory.save()
                instance.save()
                f.save_m2m()

            request.session.pop('to_list',None)
            return HttpResponse('createdlisting')
    ctx = {
        'form':form
    }
    return render(request,'test.html',ctx)