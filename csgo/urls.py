from django.urls import path,include
from . import views

from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'item',views.ItemViewSet)
router.register(r'listing',views.ListingViewSet)

app_name = 'csgo'

base_patterns = [
    path('',views.Index.as_view()),

]

listing_patterns = [
    path('list/',views.ListingListView.as_view()),
    path('create/',views.ListingCreateView.as_view()),
    path('detail/<str:pk>/',views.ListingDetailView.as_view(),name='detail'),
    path('delete/<str:pk>/',views.ListingDeleteView.as_view()),
    path('update/<str:pk>/',views.ListingUpdateView.as_view()),
]


urlpatterns = [
    path('',include(base_patterns)),
    path('listing/', include(listing_patterns),name='listing'),
    # path('api/', include(router.urls)), #API disabled for now
]
