from django.http import JsonResponse
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from api.permissions import IsOwnerOrReadOnly


from .serializers import UserSerializer
from .steam_auth import auth,get_uid,associate_user

USER_MODEL = get_user_model()

def steam_login(request):
    return auth()

def steam_callback(request):
    uid = get_uid(request.GET)
    data =  {'token':None}
    if not uid:
        return JsonResponse(data,status=400)
    else:
        user = associate_user(uid)
        data['token'] = user.get_token()
    return JsonResponse(data)

class UserViewSet(ReadOnlyModelViewSet):
    queryset = USER_MODEL.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly ]

    @action(detail=False,methods=['GET'],permission_classes=[IsAuthenticated,IsOwnerOrReadOnly])
    def my_user(self,request):
        user = request.user
        serilizer = UserSerializer(user)
        return Response(serilizer.data)
