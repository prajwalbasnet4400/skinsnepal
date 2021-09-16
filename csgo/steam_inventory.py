from django.contrib.auth import get_user_model
import requests
from django.utils.html import strip_tags

class Inventory:
    steam_inventory_api = "https://steamcommunity.com/inventory/{steamid}/730/2?l=english"
    steam_icon_url = "https://community.akamai.steamstatic.com/economy/image/{icon_url}"
    clean_fields = ['currency','background_color','type','market_name','name','name_color','tags','appid','market_actions','descriptions','market_tradable_restriction']

    def __init__(self,steamid):
        self.steamid = steamid
        self.inventory = self.steam_inventory_api.format(steamid=self.steamid)
        self.inventory = requests.get(self.inventory).json()
    
    @staticmethod
    def is_marketable(item):
        if not item.get('actions',None) or not item.get('marketable',None):
            return False
        return True

    @staticmethod
    def clean_item(item,keys=clean_fields):                                 # Very buggy, Throws random errors
        for key in keys:
            item.pop(key,None)
    
    def format_inspect_url_inplace(self,item):
        steamid = str(self.steamid)
        assetid = str(item['assetid'])
        url = item.get('actions')
        if not url:
            return None
        url = url[0]['link']
        item['inspect_url'] = url.replace(f"%owner_steamid%", steamid).replace(f"%assetid%", assetid)

    def format_icon_inplace(self,item):
        icon = item.get('icon_url')
        icon_large = item.get('icon_url_large',icon)
        
        item['icon_url'] = self.steam_icon_url.format(icon_url=icon)
        item['icon_url_large'] = self.steam_icon_url.format(icon_url=icon_large)
        
    def format_sticker_inplace(self,item):
        sticker = item.get('descriptions')
        if len(sticker) < 6:                                               # Check if the item has stickers in it
            return None
        sticker = strip_tags(sticker[-1]['value'])                         # Remove html tags from the sticker data and get csv names
        sticker = sticker.split(',')
        if " " in sticker:
            sticker.remove(" ")
        item['stickers'] = sticker
        

    def get_data(self):
        assets = {f"{mydict['assetid']}":mydict for mydict in self.inventory["assets"]}
        descriptions = {f"{mydict['classid']}":mydict for mydict in self.inventory["descriptions"]}

        for key,val in assets.copy().items():
            cid = val['classid']
            assets[key] = descriptions[cid]                                 # Remove asset dict values and insert its corresponding description
            assets[key]['assetid'] = key                                    # Add the assetid as key to description data
            item = assets[key]            

            self.format_inspect_url_inplace(item)
            self.format_icon_inplace(item)
            self.format_sticker_inplace(item)

            if not self.is_marketable(assets[key]):
                assets.pop(key)
                continue
        self.data = assets
        return assets
    
    # def save_model(self,user):
    #     i=0
    #     ThroughModel = InventoryItem.addons.through
    #     inv_obs = []
    #     addon_obs = []
    #     for val in self.data.values():
    #         item = Item.objects.filter(market_hash_name=val.get('market_hash_name'))
    #         if not item.exists():
    #             continue
    #         inv_item = InventoryItem(owner=user,item = item.first(),classid=val['classid'],
    #                             instanceid=val['instanceid'],assetid=val['assetid'],tradable=val['tradable'],inspect_url=val['inspect_url'])
    #         inv_obs.append(inv_item)
    #     InventoryItem.objects.bulk_create(inv_obs,ignore_conflicts=True)
    #     for obj in inv_obs:
    #         if not obj.pk:
    #             i = i+1
    #             print(i)

    #             continue
    #         data = self.data 
    #         assetid = data[obj.assetid]
    #         stickers = assetid.get('stickers')
    #         for sticker in stickers:
    #             try:
    #                 query = Item.objects.get(name__icontains=sticker)
    #             except Item.DoesNotExist:
    #                 continue
    #             addon_obs.append(query)
    #         obj.addons.add(addon_obs)

if __name__ == "__main__":
    from timeit import default_timer as timer
    user = get_user_model().objects.first()
    tok = Inventory(user.steamid())
    tok.get_data()
    tok.save_model(user)
    print(len(tok.data))