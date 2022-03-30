from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from csgo.models import CartItem, InventoryItem, Item, Listing

USER_MODEL = get_user_model()


class TestModel():
    """
        Class to create initial test data for database.
        Use this instead of fixtures for greater transparency
    """
    def __init__(self) -> None:
        self.user = USER_MODEL.objects.create(
            username='test_user_1',
            avatar='https://avatars.cloudflare.steamstatic.com/264a3bf942e51db3e8d1a960573b4e6dda124c5f_full.jpg',
            steamid64 = '76561198323043075',
            phone='0000000000')
        self.item = Item.objects.create(
            name=" Aquamarine Revenge ",
            market_hash_name="AK-47 | Aquamarine Revenge (Battle-Scarred)",
            type="Weapon",
            sub_type="AK-47",
            weapon_type="Rifle",
            exterior="Battle-Scarred",
            rarity="Covert",
            rarity_color="eb4b4b",
            tournament=False,
            icon_url="-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV09-5gZKKkPLLMrfFqWNU6dNoxL3H94qm3Ffm_RE6amn2ctWXdlI2ZwqB-FG_w-7s0ZK-7cjLzyE37HI8pSGKrIDGOAI",
            icon_url_large="-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV09-5gZKKkPLLMrfFqWNU6dNoxL3H94qm3Ffm_RE6amn2ctWXdlI2ZwqB-FG_w-7s0ZK-7cjLzyE37HI8pSGKrIDGOAI",
            stattrak=False,
            souvenir=False
        )
        self.inventoryitem = InventoryItem.objects.create(
            owner=self.user,
            item=self.item,
            classid=1,
            assetid=1,
            instanceid=1,
            paintindex=1,
            paintseed=1,
            defindex=1,
            item_state=InventoryItem.ItemStateChoices.INV,
            inspect_url='https://example.com',
            float=0.1
        )
        self.listing = Listing.objects.create(
            owner=self.user,
            inventory=self.inventoryitem,
            price=1,
        )
        self.cartitem = CartItem.objects.create(owner=self.user,listing=self.listing)


class IndexViewTest(TestCase):
    def setUp(self):
        self.url = reverse('csgo:index')
        self.client = Client()

    def test_index_get(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)


class ListingBuyViewTest(TestCase):
    def setUp(self):
        self.url = reverse('csgo:shop')
        self.client = Client()

    def test_listing_list_get(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)


class ListingDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_data = TestModel()
        cls.user = test_data.user
        cls.listing = test_data.listing

    def setUp(self):
        self.url = reverse('csgo:detail', kwargs={'pk': self.listing.pk})
        self.client = Client()
        self.client.force_login(self.user)

    def test_listing_detail_get(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    # Add to cart method
    def test_listing_detail_post(self):
        response = self.client.post(self.url)
        self.assertEqual(302, response.status_code)

    def test_absolute_url(self):
        absolute_url = self.listing.get_absolute_url()
        self.assertEqual(self.url, absolute_url)


class ListingDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_data = TestModel()
        cls.user = test_data.user
        cls.listing = test_data.listing

    def setUp(self):
        self.url = reverse('csgo:delete', kwargs={'pk': self.listing.pk})
        self.client = Client()
        self.client.force_login(self.user)

    def test_listing_delete_get(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    # Add to cart method
    def test_listing_delete_post(self):
        response = self.client.post(self.url)
        self.assertEqual(302, response.status_code)


class InventoryListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_data = TestModel()
        cls.user = test_data.user

    def setUp(self):
        self.url = reverse('csgo:inventory')
        self.client = Client()
        self.client.force_login(self.user)

    def test_inventory_list_get(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)


class ListingCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_data = TestModel()
        cls.user = test_data.user
        cls.inventoryitem = test_data.inventoryitem

    def setUp(self):
        self.url = reverse('csgo:inventory_create', kwargs={
                           'pk': self.inventoryitem.pk})
        self.client = Client()
        self.client.force_login(self.user)

    def test_inventory_create_get(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_inventory_create_post(self):
        data = {'price': 100}
        response = self.client.post(self.url, data)
        self.assertIsInstance(self.inventoryitem.listing, Listing)
        self.assertEqual(302, response.status_code)


class InventoryUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_data = TestModel()
        Item.get_update()
        cls.user = test_data.user

    def setUp(self):
        self.url = reverse('csgo:inventory_update')
        self.client = Client()
        self.client.force_login(self.user)

    def test_inventory_update_post(self):
        response = self.client.post(self.url)
        self.assertEqual(302, response.status_code)


class CartViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_data = TestModel()
        cls.user = test_data.user

    def setUp(self):
        self.url = reverse('csgo:cart')
        self.client = Client()
        self.client.force_login(self.user)

    def test_cart_get(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

class CartDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_data = TestModel()
        cls.user = test_data.user
        cls.cartitem = test_data.cartitem

    def setUp(self):
        self.url = reverse('csgo:cart_delete',kwargs={'pk':self.cartitem.pk})
        self.client = Client()
        self.client.force_login(self.user)

    def test_cart_delete_post(self):
        response = self.client.post(self.url)
        self.assertEqual(302,response.status_code)

class ChatManageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_data = TestModel()
        cls.user = test_data.user
        cls.listing = test_data.listing

    def setUp(self):
        self.url = reverse('csgo:chat_offer',kwargs={'pk':self.listing.pk})
        self.client = Client()
        self.client.force_login(self.user)

    def test_post_get(self):
        response = self.client.post(self.url)
        self.assertEqual(302,response.status_code)