from django.contrib import admin
from django.urls import path,include
import debug_toolbar

urlpatterns = [
    path('chat/', include('chat.urls'),name='chat'),
    path('',include('csgo.urls'),name='csgo'),
    path('user/',include('user.urls'),name='user'),
    # path('api/',include('api.urls'),name='api'),
    # path('message/',include('message.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('admin/', admin.site.urls),
]
