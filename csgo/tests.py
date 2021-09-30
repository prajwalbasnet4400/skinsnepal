from django.test import TestCase
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
import requests

from .api_parsers.steam_inventory import Inventory
from .models import InventoryItem, Item,Listing, Transaction
from .logic.trade import TradeLogic


class InventoryIntegrationTest(TestCase):
    
    def setUp(self):
        user = get_user_model()
        user_instance = user.objects.create(
            email='test@demo.com',
            username='test',
            password='test'
            )
        social_user = UserSocialAuth(
            user=user_instance,
            provider='steam',
            uid = 76561198323043075
            )
        social_user.save()
        self.user = user_instance
        
        Item.get_update()
        inventory = Inventory(user_instance)
        inventory.update_inventory()
    
    # Item test
    def test_item_availability(self,item_name='AK-47 | Aquamarine Revenge (Factory New)'):
        item = Item.objects.filter(market_hash_name=item_name).exists()
        self.assertTrue(item)

    def test_item_icon(self,item_name='AK-47 | Aquamarine Revenge (Factory New)'):
        item = Item.objects.get(market_hash_name=item_name)
        icon = item.get_icon_small()
        response = requests.get(icon)
        status_code = response.status_code
        self.assertEqual(status_code,200)

    # Inventory Test
    def test_update_inventory(self):
        sticker_check = InventoryItem.objects.filter(item__market_hash_name='P90 | Ancient Earth (Factory New)')
        self.assertAlmostEqual(sticker_check.first().float,	0.04951510578393936,msg='Item float error')
        self.assertTrue(sticker_check.first().addons.all().exists())


class TradeLogicIntegrationTest(TestCase):
    def setUp(self):
        Item.get_update()
        user = get_user_model()
        
        seller = user.objects.create(email='tok@demo.com',username='tok',password='test')
        UserSocialAuth.objects.create(user=seller,provider='steam',uid = 76561198323043075)
        buyer = user.objects.create(email='unlocky@demo.com',username='unlocky',password='test')
        UserSocialAuth.objects.create(user=buyer,provider='steam',uid = 76561199203330843)
        
        self.seller = seller
        self.buyer = buyer

        inventory = Inventory(seller)
        inventory.update_inventory()

        mp7=Item.objects.get(market_hash_name='MP7 | Forest DDPAT (Field-Tested)')
        item = InventoryItem.objects.get(item=mp7,float=0.3053702414035797,paintseed=409)

        listing = Listing(
            owner=seller,
            inventory=item,
            price=20,
            purpose=Listing.SEL)
        listing.save()
        self.tradelogic = TradeLogic(buyer,seller,listing)
        self.transaction = Transaction.objects.get(buyer=buyer,listing=listing)

    def test_inventoryitem_state(self):
        item = InventoryItem.objects.get(item__market_hash_name='MP7 | Forest DDPAT (Field-Tested)',float=0.3053702414035797,paintseed=409)
        self.assertEqual(item.item_state,InventoryItem.TRA)
        self.assertEqual(item.in_inventory,True)
