from rest_framework.routers import DefaultRouter
from django.urls import path,include
from . import views

router = DefaultRouter()
router.register('listing',views.ListingViewSet)
router.register('cart',views.CartItemViewSet)
router.register('inventory',views.InventoryItemViewSet)
router.register('transaction',views.TransactionViewSet)
router.register('wallet-transaction',views.WalletTransactionViewSet)
router.register('khalti-transaction',views.KhaltiTransactionViewSet)


app_name = 'api'
v1_patterns = [
    path('user/',include('user.urls'),name='user'),

] + router.urls

urlpatterns = [
    path('v1/',include(v1_patterns)),
] 
