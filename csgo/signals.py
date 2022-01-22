from django.db.models.signals import pre_save
from django.dispatch import receiver

from message.models import Notification

from .models import Transaction


@receiver(pre_save,sender=Transaction)
def notify_transaction(sender,instance, **kwargs):
    if instance.pk:
        Notification.objects.create(recipient=instance.listing.owner,title='Transaction State Update',content='TEST')        
        Notification.objects.create(recipient=instance.buyer,title='Transaction State Update',content='TEST')
    else:
        transaction = Transaction.objects.get(pk=instance.pk)
        if transaction.state != instance.state:
            Notification.objects.create(recipient=instance.listing.owner,title='Transaction State Update',content='TEST')        
            Notification.objects.create(recipient=instance.buyer,title='Transaction State Update',content='TEST')
