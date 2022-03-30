import requests
from django.utils.html import strip_tags
from django.conf import settings
from csgo.models import Item, InventoryItem, Addon


class InventoryItemLogic:
    steam_inventory_api = "https://steamcommunity.com/inventory/{steamid64}/730/2?l=english"
    float_api = settings.FLOAT_API
    exclude_fields = ['appid', 'currency',
                      'background_color', 'market_buy_country_restriction', 'market_name']

    def __init__(self, user):
        self.user = user
        self.steamid = user.steamid()
        self.inv_api_url = self.steam_inventory_api.format(
            steamid64=self.steamid)

    def get_inventory_data(self):
        """
            Retrive all items in player's csgo inventory from the steam api
        """
        response = requests.get(self.inv_api_url)
        data = response.json()
        return data

    def update_inventory(self):
        """
            Populate / Update a User's InventoryItems from the api
        """
        self.update_inventory_wrapper(self.get_inventory_data())

    def update_inventory_wrapper(self, inventory_api_response_json):
        assets = inventory_api_response_json['assets']
        descriptions = inventory_api_response_json['descriptions']

        # For storing all InventoryItems' market_hash_name and
        # querying all of them at once to save sql queries
        market_hash_name_list = set()
        # For matching assets' with their respective description
        descriptions_map = {}
        # Store InventoryItem objects for bulk creation
        inventory_item_objs = []
        # Store Addon objects for bulk creation
        addon_objs = []
        # Get list of assetid of all inventory item of the user
        # to avoid duplicate entry
        existing_inv_item_assetids = self.get_existing_inventory_item()
        # For cleaning InventoryItems which no longer exist
        # in the user's steam inventory
        asset_ids = []

        for desc in descriptions:
            # Get stickers' names
            desc['stickers'] = self.format_sticker(desc)

            # Remove unwanted keys
            cleaned_desc = self.clean_fields(desc)
            # Add the cleaned data to the descriptions_map
            descriptions_map[f"{desc['classid']}_{desc['instanceid']}"] = cleaned_desc

            market_hash_name_list.add(desc['market_hash_name'])

            # If stickers exist, add their market name to the preload Item list
            
            for sticker in desc['stickers']:
                market_hash_name_list.add(sticker)

        items = self.preload_item(market_hash_name_list)

        for asset in assets:
            asset_ids.append(asset['assetid'])
            
            # If InventoryItem already exists, skip creating this object
            if asset['assetid'] in existing_inv_item_assetids:
                continue

            description = descriptions_map[f"{asset['classid']}_{asset['instanceid']}"]
            description['assetid'] = asset['assetid']

            if not self.is_marketable(description):
                continue

            # Formatting data
            description['inspect_url'] = self.format_inspect_url(
                self.steamid, description)
            item_details = self.get_item_detail(description['inspect_url'])
            description['float'] = item_details.get('floatvalue', 0)
            description['defindex'] = item_details.get('defindex', 0)
            description['paintindex'] = item_details.get('paintindex', 0)
            description['paintseed'] = item_details.get('paintseed', 0)

            inv_item = self.construct_inventory_item(description, items)
            inventory_item_objs.append(inv_item)

        inv_items = self.create_inventory_item_bulk(inventory_item_objs)

        # Create stickers for the respective InventoryItem if it sticker exists
        for obj in inv_items:
            if not obj.pk:
                continue
            stickers = descriptions_map[f"{obj.classid}_{obj.instanceid}"]['stickers']
            for sticker in stickers:
                item = items.get(sticker)
                if item:
                    addon = Addon(item=item, inventory=obj)
                    addon_objs.append(addon)

        # Create addons objs in bulk
        self.create_addons_bulk(addon_objs)
        

        self.clean_old_items(asset_ids)

    def clean_old_items(self, asset_ids):
        """
            Delete non existing items in inventory in db //
            If its sold dont change its status        
        """
        excluded_items = InventoryItem.objects.filter(owner=self.user)
        excluded_items = excluded_items.exclude(assetid__in=asset_ids)
        excluded_items.update(in_inventory=False)
        excluded_items = excluded_items.filter(item_state__in=[
                                               InventoryItem.ItemStateChoices.LIS, InventoryItem.ItemStateChoices.INV])
        excluded_items.delete()

    def construct_inventory_item(self, description, items):
        if not items.get(description['market_hash_name']):
            return None
        return InventoryItem(
            owner=self.user,
            item=items.get(description['market_hash_name']),
            classid=description['classid'],
            instanceid=description['instanceid'],
            assetid=description['assetid'],
            tradable=description['tradable'],
            inspect_url=description['inspect_url'],
            float=description['float'],
            paintindex=description['paintindex'],
            paintseed=description['paintseed'],
            defindex=description['defindex']
        )

    def clean_fields(self, description):
        """
            Remove unwanted fields from the description
        """
        fields = self.exclude_fields
        for field in fields:
            try:
                description.pop(field)
            except:
                pass
        return description

    def get_item_detail(self, inspect_url):
        """
            Retrive float, paintseed, paintindex, defindex from the float api
            Reference: https://github.com/csgofloat/inspect#api
        """
        url = self.float_api.format(inspect_url=inspect_url)
        response = requests.get(url, timeout=3)
        data = response.json()
        data = data.get('iteminfo', {})
        return data

    def get_existing_inventory_item(self):
        """
            Get a list of assetids of inventory item already in list
        """
        return InventoryItem.objects.filter(owner=self.user).values_list('assetid', flat=True)

    @staticmethod
    def preload_item(market_hash_name_list):
        """
            Get all Item objects in bulk referenced in the market_hash_name_list
        """

        items = Item.objects.in_bulk(
            market_hash_name_list, field_name='market_hash_name')
        return items

    @staticmethod
    def create_inventory_item_bulk(inv_items):
        return InventoryItem.objects.bulk_create(inv_items)

    @staticmethod
    def create_addons_bulk(addon_objs):
        return Addon.objects.bulk_create(addon_objs, ignore_conflicts = True)

    @staticmethod
    def is_marketable(description):
        """
            Check if the item is allowed in the marketplace or not
        """

        if not description.get('actions', None) or not description.get('marketable', None):
            return False
        if description.get('commodity') == 1:
            return False
        return True

    @staticmethod
    def format_inspect_url(steamid64, description):
        """
            Format the inspect url with the user's steamid and InventoryItem's assetid
        """
        steamid64 = str(steamid64)
        assetid = str(description['assetid'])
        url = description.get('actions')

        # If inspect_url doesn't exist, return none
        if not url:
            return None
        url = url[0]['link']

        # Replace the steamid64 and assetid in the inspect url to construct a valid inspect url
        return url.replace(f"%owner_steamid%", steamid64).replace(f"%assetid%", assetid)

    @staticmethod
    def format_sticker(description):
        """
            Extract stickers' data from the description.
            Returns a sticker's list with their queryable market_hash_name
        """

        stickers = description.get('descriptions')
        # Check if the item has stickers in it
        if len(stickers) < 6:
            return []

        # Remove html tags from the stickers data and get comma separated names
        stickers = strip_tags(stickers[-1]['value'])
        stickers = stickers.split(',')

        # The first name contains unwanted data, so clean it separately
        stickers[0] = stickers[0].split(':')[-1]

        # Remove blank strings from stickers' list
        try:
            stickers.remove(" ")
            stickers.remove("")
        except ValueError:
            pass

        # The Stickers' name doesn't match their market_hash_name
        # because of missing 'Sticker | ' at the start, so add it
        for i, sticker in enumerate(stickers):
            stickers[i] = f"Sticker | {sticker.strip()}"
        return stickers