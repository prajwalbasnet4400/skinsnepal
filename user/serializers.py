from django.contrib.auth import get_user_model
from rest_framework import serializers

USER_MODEL = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER_MODEL
        fields = ['id','username','first_name','last_name','phone','credit','avatar']
