from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import login, get_user_model

from .steam_auth import auth,get_uid,associate_user

USER_MODEL = get_user_model()

def steam_login_url(request):
    return auth(reverse('user:steam_callback_session'))

def steam_callback_session(request):
    uid = get_uid(request.GET)
    if not uid:
        return redirect('csgo:index')
    else:
        user = associate_user(uid)
        login(request,user,'django.contrib.auth.backends.ModelBackend')
        return redirect('csgo:index')

def steam_callback(request):
    uid = get_uid(request.GET)
    data =  {'token':None}
    if not uid:
        return JsonResponse(data,status=400)
    else:
        user = associate_user(uid)
        data['token'] = user.get_token()
    return JsonResponse(data)