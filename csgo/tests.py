from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
import requests

from .steam_inventory import Inventory
from .parsers import get_csgo_items
from .models import InventoryItem, Item,Listing
from user.models import User

class InventoryTest(TestCase):
    
    def setUp(self):
        self.ins_success = Inventory(76561198323043075)
        self.ins_failure = Inventory(123123123)

    def test_inventory_get(self):
        ins_success_result = self.ins_success.inventory.get('success',None)
        ins_failure_result = self.ins_failure.inventory
        
        self.assertTrue(ins_success_result)
        self.assertEqual(ins_failure_result,None)

    def test_get_data(self):
        data = self.ins_success.get_data()
        ins_success_result = data.get('22338649298',None)
        ins_failure_result = data.get('15392788641',None)

        self.assertNotEqual(ins_success_result,None)
        self.assertEqual(ins_failure_result,None)

class ParserTest(TestCase):
    
    def test_csgoback_api(self,no_items=14000):
        items = get_csgo_items()
        length = len(items)

        self.assertNotEqual(items,None)
        self.assertGreater(length,no_items)
    
class ItemTest(TestCase):

    def setUp(self):
        Item.get_update()

    def test_item_availability(self,item_name='AK-47 | Aquamarine Revenge (Factory New)'):
        item = Item.objects.filter(market_hash_name=item_name).exists()

        self.assertTrue(item)

    def test_item_icon(self,item_name='AK-47 | Aquamarine Revenge (Factory New)'):
        item = Item.objects.get(market_hash_name=item_name)
        icon = item.get_icon_small()

        response = requests.get(icon)
        status_code = response.status_code

        self.assertEqual(status_code,200)
    
    def test_str(self,item_name='AK-47 | Aquamarine Revenge (Factory New)'):
        item = Item.objects.get(market_hash_name=item_name)
        self.assertEqual(item.__str__(),item.market_hash_name)
        

class ListingTest(TestCase):

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
        Listing.objects.create(
                owner= user_instance,
                item=Item.objects.create(
                name='Aquamarine Revenge',
                market_hash_name='AK-47 | Aquamarine Revenge (Factory New)',
                icon_url='''-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV09
                            -5gZKKkPLLMrfFqWdY781lxLuW8Njw31Dn8xc_YTqmJ4DDJFM2ZwqE_ATtx-u7g8C5vpjOzHM263E8pSGKJ1XuG9M''',
                type='Weapon',
                sub_type='AK-47',
                exterior='Factory New',
                rarity='Covert',
                rarity_color='eb4b4b',
                ),
            float=0.003,
            price=200
            )
        self.user = User.objects.first() 
        self.listing = Listing.objects.first()
        Item.get_update()
        InventoryItem.update_inventory(self.user)


    def test_inventory_listing(self):
        inv_item = InventoryItem.objects.first()
        listing = Listing.objects.create(
            owner=self.user,
            item=inv_item.item,
            inventory=inv_item,
            classid=inv_item.classid,
            instanceid=inv_item.instanceid,
            assetid=inv_item.assetid,
            float=inv_item.float,
            price=200,
            tradable=inv_item.tradable,
            inspect_url=inv_item.inspect_url
            )
        self.assertIsInstance(listing,Listing)
        
        inv_item.is_listed = True
        inv_item.save()
        listing.delete()

        inv_item = InventoryItem.objects.filter(owner=self.user).first()
        listed_status = inv_item.is_listed
        self.assertFalse(listed_status)

    def test_str(self):
        listing = Listing.objects.first()
        self.assertEqual(listing.__str__(),listing.item.market_hash_name)




