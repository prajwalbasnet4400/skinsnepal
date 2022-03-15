from django.contrib import admin
from django.urls import path,include
import debug_toolbar

urlpatterns = [
    path('',include('csgo.urls'),name='csgo'),
    path('chat/', include('chat.urls'),name='chat'),
    path('user/',include('user.urls'),name='user'),
    path('__debug__/', include(debug_toolbar.urls)),
    path('admin/', admin.site.urls),
]
