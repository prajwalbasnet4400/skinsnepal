from django.test import TestCase
from csgo.logic.parsers import get_csgo_items, get_item_price

class TestGetCsgoItems(TestCase):
    def test_get_csgo_items(self):
        items = get_csgo_items()
        self.assertGreater(len(items),1000)

class TestGetItemPrice(TestCase):
    def test_get_item_price(self):
        name = 'AK-47 | Aquamarine Revenge (Factory New)'
        item = get_item_price(name=name)
        self.assertEqual(item.get('success'),True)