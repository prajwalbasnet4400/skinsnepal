from django.contrib import admin
from django.urls import path,include
import debug_toolbar

urlpatterns = [
    path('api/',include('api.urls'),name='api'),
    path('csgo/',include('csgo.urls')),
    path('message/',include('message.urls')),
    
    path('__debug__/', include(debug_toolbar.urls)),
    path('admin/', admin.site.urls),
]
