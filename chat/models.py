from django.db import models
from django.contrib.auth import get_user_model

USER_MODEL = get_user_model()

class Room(models.Model):
    user = models.ManyToManyField(USER_MODEL,related_name='rooms')
    group = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.pk}'
    
    def get_room_user(self,of_user:USER_MODEL):
        return self.user.exclude(of_user).first()

class Message(models.Model):
    class StatusChoices(models.TextChoices):
        SENT = "SENT", "SENT"
        DELI = "DELIVERED", "DELIVERED"
        SEEN = "SEEN", "SEEN"
        DELE = "DELETED", "DELETED"
        HIDD = "HIDDEN", "HIDDEN"
        
    room = models.ForeignKey(Room,on_delete=models.CASCADE,related_name='messages')
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=64)
    content = models.CharField(max_length=5000)
    status = models.CharField(max_length=64,choices=StatusChoices.choices,default=StatusChoices.SENT)
    date_sent = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.username
    
    def steamid64(self):
        return self.user.steamid64