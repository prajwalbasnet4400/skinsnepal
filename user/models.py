from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.authtoken.models import Token

class User(AbstractUser):
    steamid64 = models.CharField(max_length=17,unique=True,null=False,blank=False)
    avatar = models.URLField(blank=True)
    phone = models.CharField(max_length=15,null=True,blank=True)
    credit = models.PositiveIntegerField(default=0)
    
    def get_token(self):
        token, created = Token.objects.get_or_create(user=self)
        return token.key

    def steamid(self):
        return self.steamid64

    def add_credit(self,to_add):
        self.credit = self.credit + to_add
        return self.credit

    def get_steam_url(self):
        return f"https://steamcommunity.com/profiles/{self.steamid64}"

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    trade_url = models.URLField(null=True,blank=True)

    def __str__(self):
        return self.user.username