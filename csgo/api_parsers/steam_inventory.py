import requests
from django.utils.html import strip_tags
from csgo.models import Item, InventoryItem, InventoryAddon


class Inventory:
    steam_inventory_api = "https://steamcommunity.com/inventory/{steamid}/730/2?l=english"
    steam_icon_url = "https://community.akamai.steamstatic.com/economy/image/{icon_url}"
    float_api = "http://127.0.0.1/?url={inspect_url}"
    clean_fields = ['currency','background_color','type','market_name','name','name_color','tags','appid','market_actions','descriptions','market_tradable_restriction']

    def __init__(self,user):
        self.user = user
        self.steamid = user.steamid()
        self.inventory = self.steam_inventory_api.format(steamid=self.steamid)
        self.inventory = requests.get(self.inventory).json()
        self.data = None
    
    @staticmethod
    def _is_marketable(item):
        if not item.get('actions',None) or not item.get('marketable',None):
            return False
        if item.get('commodity') == 1:
            return False
        return True
    
    def _get_item_detail(self,inspect_url):
        url = self.float_api.format(inspect_url=inspect_url)
        r = requests.get(url,timeout=3)
        data = r.json()
        data = data.get('iteminfo',{})
        return data

    def _format_inspect_url(self,item):
        steamid = str(self.steamid)
        assetid = str(item['assetid'])
        url = item.get('actions')
        if not url:
            return None
        url = url[0]['link']
        item['inspect_url'] = url.replace(f"%owner_steamid%", steamid).replace(f"%assetid%", assetid)

    def _format_icon(self,item):
        icon = item.get('icon_url')
        icon_large = item.get('icon_url_large',icon)
        
        item['icon_url'] = self.steam_icon_url.format(icon_url=icon)
        item['icon_url_large'] = self.steam_icon_url.format(icon_url=icon_large)
        
    def _format_sticker(self,item):
        sticker = item.get('descriptions')
        if len(sticker) < 6:                                               # Check if the item has stickers in it
            return None
        sticker = strip_tags(sticker[-1]['value'])                         # Remove html tags from the sticker data and get csv names
        sticker = sticker.split(',')
        sticker[0] = sticker[0].split(':')[-1]
        if " " in sticker:
            sticker.remove(" ")
        item['stickers'] = sticker
        

    def get_data(self):
        if not self.inventory.get('assets',None):
            self.data = {}
            return {}
        assets = {f"{mydict['assetid']}":mydict for mydict in self.inventory["assets"]}
        descriptions = {f"{mydict['classid']}":mydict for mydict in self.inventory["descriptions"]}

        for key,val in assets.copy().items():
            assets[key].update(descriptions[val['classid']])

            if not self._is_marketable(assets[key]):
                assets.pop(key)
                continue

            self._format_inspect_url(assets[key])
            self._format_icon(assets[key])
            self._format_sticker(assets[key])
            item_detail =self._get_item_detail(assets[key].get('inspect_url'))
            assets[key]['paintindex'] = item_detail.get('paintindex',0)
            assets[key]['paintseed'] = item_detail.get('paintseed',0)
            assets[key]['float'] = item_detail.get('floatvalue',0)
            assets[key]['defindex'] = item_detail.get('defindex',0)

        self.data = assets
        return assets

    def update_inventory(self):
        if not self.data:
            self.get_data()
        data = self.data
        objs = []
        assetids = []
        names = set()
        sticker_names = set()

        for item in data.values():
            assetids.append(item['assetid'])
            names.add(item['market_hash_name'])
            for sticker in item.get('stickers',[]):
                sticker_names.add(sticker)

        existing_items = Item.objects.in_bulk(names,field_name='market_hash_name')
        existing_inv = InventoryItem.objects.filter(assetid__in=assetids).values_list('assetid',flat=True)

        for item in data.values():
            if not item.get('market_hash_name') in existing_items.keys():
                continue
            if item.get('assetid') in existing_inv:
                continue
            inv =InventoryItem(
                owner=self.user,
                item=existing_items.get(item['market_hash_name']),
                classid=item['classid'],
                instanceid=item['instanceid'],
                assetid=item['assetid'],
                tradable=item['tradable'],
                inspect_url=item['inspect_url'],
                float=item['float'],
                paintindex=item['paintindex'],
                paintseed=item['paintseed']
                )
            objs.append(inv)
        objs = InventoryItem.objects.bulk_create(objs)

        for obj in objs:                                # Stickers m2m field logic
            data_stickers = data[obj.assetid]
            for sticker in data_stickers.get('stickers',[]):
                if sticker not in sticker_names:
                    continue
                InventoryAddon.objects.create(
                    inventory=obj,
                    addon=Item.objects.filter(type='Sticker',market_hash_name__icontains=sticker).first()
                )
        
        excluded_items = InventoryItem.objects.exclude(assetid__in=[assetids])
        excluded_items = excluded_items.filter(owner=self.user,item_state__in=[InventoryItem.INV,InventoryItem.LIS])