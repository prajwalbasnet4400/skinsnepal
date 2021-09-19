from django.conf import settings
from django.contrib import admin
from django.urls import path,include
import debug_toolbar


urlpatterns = [
    path('',include('csgo.urls')),
    path('account/',include('user.urls')),

    path('auth/social/', include('social_django.urls', namespace='social')),
    path("select2/", include("django_select2.urls")),

    path('__debug__/', include(debug_toolbar.urls)),
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.authtoken')),

    path('admin/', admin.site.urls),
]
