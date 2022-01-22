from django.urls import path
from . import views

app_name = 'csgo'

urlpatterns = [
    path('shop/',views.ListingBuyView.as_view(),name='shop'),
    
    path('detail/<uuid:uuid>/',views.ListingDetailView.as_view(),name='detail'),
    path('delete/<uuid:uuid>/',views.ListingDeleteView.as_view(),name='delete'),
    
    path('inventory/', views.InventoryListView.as_view(),name='inventory'),
    path('inventory/create/', views.ListingCreateView.as_view(),name='inventory_create'),
    path('inventory/create/to_list/', views.InventoryToList.as_view(),name='to_list'),

    path('cart/', views.CartView.as_view(),name='cart'),
    path('cart/add/', views.CartAddView.as_view(),name='cart_add'),
    path('cart/delete/', views.CartDeleteView.as_view(),name='cart_delete'),
    path('cart/checkout/', views.CheckOutView.as_view(),name='checkout'),



    path('transactions/', views.TransactionListView.as_view(),name='transaction_list'),
    path('transaction/<str:pk>/', views.TransactionDetailView.as_view(),name='transaction'),
    
    path('wallet/', views.WalletView.as_view(),name='wallet_list'),

    path('get_item_prices/',views.get_item_price_view,name='price'),
    path('test/',views.test)
    
]
