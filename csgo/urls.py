from django.urls import path,include
from . import views

app_name = 'csgo'

listing_patterns = [
    path('shop/',views.ListingBuyView.as_view(),name='shop'),
    path('detail/<str:pk>/',views.ListingDetailView.as_view(),name='detail'),
    path('delete/<str:pk>/',views.ListingDeleteView.as_view(),name='delete'),
]

cart_patterns = [
    path('', views.CartView.as_view(),name='cart'),
    path('delete/', views.CartDeleteView.as_view(),name='cart_delete'),
]

inventory_patterns = [
    path('', views.InventoryListView.as_view(),name='inventory'),
    path('create/<str:pk>/', views.ListingCreateView.as_view(),name='inventory_create'),
    path('manage/', views.InventoryManageView.as_view(),name='inventory_update'),
]

transaction_patterns = [
    path('transactions/', views.TransactionListView.as_view(),name='transaction_list'),
    path('transaction/<str:pk>/', views.TransactionDetailView.as_view(),name='transaction'),
]

wallet_patterns = [
    path('wallet/', views.WalletView.as_view(),name='wallet_list'),
]

urlpatterns = [
    path('',views.IndexView.as_view(),name='index'),
    path('item/',include(listing_patterns)),
    path('inventory/',include(inventory_patterns)),
    path('cart/',include(cart_patterns))
]