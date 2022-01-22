from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class User(AbstractUser):
    phone = models.CharField(max_length=15,null=True,blank=True)
    credit = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username

    def get_credit(self):
        return self.credit // 100

    def subtract_credit(self,amt):
        return self.credit - amt

    def add_credit(self,amt):
        return self.credit + amt

    def get_profile(self):
        try:
            return self.profile
        except ObjectDoesNotExist:
            return None

    
    def steamid(self):
        return self.social_auth.first().uid
        


class Profile(models.Model):                #TODO:add integration for steam api key
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    avatar = models.URLField()
    trade_url = models.URLField(null=True,blank=True)

    def __str__(self):
        return self.user.username