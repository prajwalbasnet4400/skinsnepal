from django.urls import path,include
from . import views

app_name = ''

auth_patterns = [
    path('signup/',views.Signup.as_view(),name='signup'),
    path('login/',views.Login.as_view(),name='login'),
    path('logout/',views.Logout.as_view(),name='logout'),
    path('password_change/',views.PasswordChange.as_view(),name='password_change'),
    path('password_change/done/',views.PasswordChangeDone.as_view(),name='password_change_done'),
    path('password_reset/',views.PasswordReset.as_view(),name='password_reset'),
    path('password_reset/done/',views.PasswordResetDone.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',views.PasswordResetConfirm.as_view(),name='password_reset_confirm'),
    path('reset/done/',views.PasswordResetDone.as_view(),name='password_reset_complete'),
]

urlpatterns = [
    path('',include(auth_patterns))
]