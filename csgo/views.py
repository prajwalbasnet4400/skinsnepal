from django.views import View
from django.views.generic import (CreateView,DetailView,DeleteView,UpdateView,ListView)
from django.shortcuts import render,redirect
from django.views.generic.base import TemplateView

from .models import Item, Listing

# REST FRAMEWORK

from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .serializers import ItemSerializer, ListingSerializer, ListingNestedSerializer
from .permissions import IsOwnerOrReadOnly,ReadOnly

class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAdminUser|ReadOnly]

class ListingViewSet(ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def list(self, request):
        queryset = self.queryset
        serializer = ListingNestedSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        return super(ListingViewSet, self).perform_create(serializer)

## REGULAR VIEWS

# Base views
class Index(View):
    template_name = 'index.html'

    def get(self,request,*args, **kwargs):
        ctx ={}
        ctx['listing_latest'] = Listing.objects.select_related('item').all().order_by('-date_created',)[:6]
        return render(request,self.template_name,ctx)

# Listing Model views
class ListingListView(ListView):
    model = Listing
    context_object_name = 'listing_list'

class ListingCreateView(CreateView):
    model = Listing
    context_object_name = 'listing'
    fields = '__all__'

class ListingDetailView(DetailView):
    model = Listing
    context_object_name = 'listing'
    fields = '__all__'

class ListingDeleteView(DeleteView):
    model = Listing
    context_object_name = 'listing'

class ListingUpdateView(UpdateView):
    model = Listing
    context_object_name = 'listing'
    fields = '__all__'
