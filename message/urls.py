from django.urls import path
from . import views

app_name = 'message'

urlpatterns = [
    path('notification_count/',views.NotificationCountView.as_view(),name='notification_count'),
    path('notification/',views.NotificationView.as_view(),name='notification'),
]
