from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15,null=True,blank=True)

class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    trade_url = models.URLField(null=True,blank=True)
