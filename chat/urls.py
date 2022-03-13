# chat/urls.py
from django.urls import path,include

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

]