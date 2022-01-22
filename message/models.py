from django.db import models
from django.contrib.auth import get_user_model

class Notification(models.Model):
    recipient = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    content = models.TextField()
    read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient}_{self.title[:10]}"