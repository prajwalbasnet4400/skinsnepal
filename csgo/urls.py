from csgo import api_views
from django.urls import path,include
from . import views
from .rest import views as rest_views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'item',rest_views.ItemViewSet)
router.register(r'listing',rest_views.ListingViewSet)

app_name = 'csgo'

base_patterns = [
    path('',views.Index.as_view(),name='index'),

]

listing_patterns = [
    path('shop/',views.ListingShopView.as_view(),name='shop'),
    path('trade/',views.ListingTradeView.as_view(),name='trade'),
    path('auction/',views.ListingAuctionView.as_view(),name='auction'),
    
    path('detail/<str:pk>/',views.ListingDetailView.as_view(),name='detail'),
    path('delete/<str:pk>/',views.ListingDeleteView.as_view(),name='delete'),
    
    path('inventory/', views.InventoryListView.as_view(),name='inventory'),
    path('inventory/create', views.InventoryCreateView.as_view(),name='inventory_create'),

    path('cart/', views.CartView.as_view(),name='cart'),
    path('checkout/<str:pk>/', views.CheckoutView.as_view(),name='checkout'),
]



urlpatterns = [
    path('',include(base_patterns)),
    path('csgo/', include(listing_patterns),name='listing'),
    
    path('item/price/<str:market_hash_name>/', api_views.get_price,name='price'),
    path('inventory/update', views.test2),
    
    # path('api/', include(router.urls)), #API disabled for now
]
