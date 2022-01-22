from message.models import Notification
from django.conf import settings

inventory_item_url =settings.INVENTORY_ITEM

class TransactionNotification:
    def __init__(self,transaction):
        self.transaction = transaction
        self.listing = transaction.listing
        self.buyer = transaction.buyer
        self.seller = transaction.listing.owner
    
    def send_state_notification(self):
        title = f"{self.transaction.state} for {self.listing}-{self.listing.pk}"
        content_seller = f"Your item {self.listing}, listed for sale has updated its state to {self.transaction.state}"
        content_buyer = f"The item {self.listing}, you bought has updated its state to {self.transaction.state}"
        Notification.objects.create(recipient=self.seller,title=title,content=content_seller)
        Notification.objects.create(recipient=self.buyer,title=title,content=content_buyer)
        
    def send_trade_send_notification(self):
        item_url = inventory_item_url.format(assetid=self.listing.inventory.assetid)
        title = f"Item sold, Send trade offer for {self.listing}-{self.listing.pk}"
        content = f"Please send trade offer for <a href='{item_url}'>{item_url}</a>. <script>alert('fak')</script>If trade offer is not sent within 24 hours, the transaction will be cancelled and you will be banned for a day"
        Notification.objects.create(recipient=self.seller,title=title,content=content)
    
    def send_trade_accept_notification(self):
        title = f"Accept trade offer for {self.listing}-{self.listing.pk}"
        content = f"Please Accept trade offer for {self.listing}. If trade offer is not accepted within 24 hours, the transaction will be cancelled and you will be banned for a day"
        Notification.objects.create(recipient=self.buyer,title=title,content=content)

    def send_payment_complete_notification(self):
        title = f"Transaction complete for {self.listing}-{self.listing.pk}"
        content = f"Thank you for choosing KhukuriMart. Your transaction has been completed and the seller has been paid after deducing for taxes and fees."
        Notification.objects.create(recipient=self.buyer,title=title,content=content)
        Notification.objects.create(recipient=self.seller,title=title,content=content)
