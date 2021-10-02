from csgo.api_parsers.steam_inventory import Inventory
from csgo.models import InventoryItem, Transaction

class TradeLogic:
    
    def __init__(self,buyer,seller,listing):
        self.buyer = buyer
        self.seller = seller
        self.listing = listing

        self.update_inv()
        self.get_inv()
        self.transaction, _ = Transaction.objects.get_or_create(buyer=buyer,listing=listing)

    def update_inv(self):
        Inventory(self.seller).update_inventory()
        Inventory(self.buyer).update_inventory()
    
    def get_inv(self):
        self.buyer_inventory = InventoryItem.objects.filter(owner=self.buyer)
        self.seller_inventory = InventoryItem.objects.filter(owner=self.seller)
        
    def buyer_paid(self):                                                   # Currently set to always True TODO: Implement payment gateway
        return self.listing.transaction.buyer_paid()

    def trade_sent(self):                                                   #Not perfect: Malicious user may list the item to market to fake this to True
        return not self.listing.inventory.in_inventory
    
    def trade_sent_screenshot_exists(self):
        if self.listing.transaction.trade_sent_screenshot is None:
            return False
        return True
    
    def trade_accepted(self):
        item = self.listing.inventory.item
        paintindex = self.listing.inventory.paintindex
        paintseed = self.listing.inventory.paintseed
        float = self.listing.inventory.float    
        return self.buyer_inventory.filter(item=item,paintindex=paintindex,paintseed=paintseed,float=float).exists()
    
    def trade_accept_screenshot_exists(self):
        if self.listing.transaction.trade_recv_screenshot is None:
            return False
        return True

    def seller_paid(self):
        return self.listing.transaction.seller_paid()

    def transaction_complete(self):
        status = self.buyer_paid() & self.trade_sent() & self.trade_sent_screenshot_exists() & self.trade_accepted() & self.trade_accept_screenshot_exists()
        return status