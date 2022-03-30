from django.db import models
from django.contrib.auth import get_user_model

USER_MODEL = get_user_model()


class Room(models.Model):
    user = models.ManyToManyField(USER_MODEL, related_name='rooms')
    group = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.pk}'


class RoomUser(models.Model):
    user = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, related_name='room_user')
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='users')

    def __str__(self):
        return f"{self.user.username}_{self.room.pk}"


class BlockedUser(models.Model):
    blocked_by = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, related_name='blocked_users')
    blocked_user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.blocked_by.username}_{self.blocked_user.username}"


class Message(models.Model):
    class StatusChoices(models.TextChoices):
        SENT = "SENT", "SENT"
        DELI = "DELIVERED", "DELIVERED"
        SEEN = "SEEN", "SEEN"
        DELE = "DELETED", "DELETED"
        HIDD = "HIDDEN", "HIDDEN"

    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=5000)
    status = models.CharField(
        max_length=64, choices=StatusChoices.choices, default=StatusChoices.SENT)
    date_sent = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.username

    @property
    def steamid64(self):
        return self.user.steamid64
