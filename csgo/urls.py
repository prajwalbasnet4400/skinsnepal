from django.urls import path,include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'item',views.ItemViewSet)
router.register(r'listing',views.ListingViewSet)

app_name = 'csgo'

urlpatterns = [
    path('', include(router.urls)),
]
