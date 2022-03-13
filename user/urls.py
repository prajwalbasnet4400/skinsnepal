from django.urls import path
# from rest_framework.routers import DefaultRouter
from . import views


# router = DefaultRouter()
# router.register('users',views.UserViewSet)

app_name = 'user'

urlpatterns = [
    path('auth/steam/', views.steam_login_url, name='steam_login'),
    path('steam_callback/session/', views.steam_callback_session, name='steam_callback_session'),
    path('steam_callback/', views.steam_callback, name='steam_callback'),
    ] 
    