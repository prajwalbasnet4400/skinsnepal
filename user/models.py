from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class User(AbstractUser):
    phone = models.CharField(max_length=15,null=True,blank=True)

    def get_profile(self):
        try:
            return self.profile
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return self.username
    
    def steamid(self):
        return self.social_auth.first().uid


class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    avatar = models.URLField()
    trade_url = models.URLField(null=True,blank=True)

    def __str__(self):
        return self.user.username