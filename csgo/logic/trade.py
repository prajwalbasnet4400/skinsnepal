from csgo.api_parsers.steam_inventory import Inventory
from csgo.models import InventoryItem, Transaction

class TradeLogic:
    
    def __init__(self,transaction):
        self.buyer = transaction.buyer
        self.seller = transaction.listing.owner
        self.listing = transaction.listing
        self.transaction = transaction

    def update_buyer_inv(self):
        Inventory(self.buyer).update_inventory()

    def update_seller_inv(self):
        Inventory(self.seller).update_inventory()

    def update_inv(self):
        self.update_buyer_inv()
        self.update_seller_inv()

    def get_inv(self):
        self.buyer_inventory = InventoryItem.objects.filter(owner=self.buyer)
        self.seller_inventory = InventoryItem.objects.filter(owner=self.seller)
        
    def buyer_paid(self):                                                   # Currently set to always True TODO: Implement payment gateway
        return self.listing.transaction.buyer_paid()

    def trade_sent(self):                                                   #Not perfect: Malicious user may list the item to market to fake this to True
        inv = Inventory(self.seller)
        exists = inv.check_item_exists(self.listing.inventory.item.market_hash_name,
                                self.listing.inventory.defindex,
                                self.listing.inventory.float,
                                self.listing.inventory.paintindex,
                                self.listing.inventory.paintseed)
        return not exists
    
    def trade_sent_screenshot_exists(self):
        if self.listing.transaction.trade_sent_screenshot is None:
            return False
        return True
    
    def trade_accepted(self):
        item = self.listing.inventory.item
        paintindex = self.listing.inventory.paintindex
        paintseed = self.listing.inventory.paintseed
        defindex = self.listing.inventory.defindex
        float = self.listing.inventory.float    
        inv = Inventory(self.buyer)
        exists = inv.check_item_exists(item.market_hash_name,
                                defindex,
                                float,
                                paintindex,
                                paintseed)
        if exists:
            return True
        else:
            return False
    
    def trade_accept_screenshot_exists(self):
        if self.listing.transaction.trade_recv_screenshot is None:
            return False
        return True

    def seller_paid(self):
        return self.listing.transaction.seller_paid()

    def transaction_complete(self):
        status = self.buyer_paid() & self.trade_sent() & self.trade_sent_screenshot_exists() & self.trade_accepted() & self.trade_accept_screenshot_exists()
        return status