from django.contrib import admin
from django.urls import path,include
import debug_toolbar

from csgo.views import IndexView

urlpatterns = [
    # Base Views
    path('',IndexView.as_view(),name='index'),

    # App Views
    path('csgo/',include('csgo.urls')),
    path('account/',include('user.urls')),
    path('message/',include('message.urls')),
    
    # Imported App views
    path('auth/social/', include('social_django.urls', namespace='social')),
    path("select2/", include("django_select2.urls")),
    path('__debug__/', include(debug_toolbar.urls)),

    path('admin/', admin.site.urls),

    
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.authtoken')),
]
