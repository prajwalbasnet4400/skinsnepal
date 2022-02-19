import requests
from django.utils.html import strip_tags
from csgo.models import Item, InventoryItem,Addon

from django.conf import settings

class Inventory:
    steam_inventory_api = "https://steamcommunity.com/inventory/{steamid}/730/2?l=english"
    steam_icon_url = "https://community.akamai.steamstatic.com/economy/image/{icon_url}"
    float_api = settings.FLOAT_API
    clean_fields = ['currency','background_color','type','market_name','name','name_color','tags','appid','market_actions','descriptions','market_tradable_restriction']

    def __init__(self,user):
        self.user = user
        self.steamid = user.steamid()
        inv_url = self.steam_inventory_api.format(steamid=self.steamid)
        self.inventory = requests.get(inv_url).json()

    def check_item_exists(self,market_hash_name,defindex,float,paintindex,paintseed):
        if self.inventory.get('total_inventory_count') == 0:
            return False
        assets = {f"{mydict['assetid']}":mydict for mydict in self.inventory["assets"]}
        descriptions = {f"{mydict['classid']}":mydict for mydict in self.inventory["descriptions"]}
        items = []
        for key, val in assets.copy().items():
            if descriptions[val['classid']]['market_hash_name'] != market_hash_name:
                assets.pop(key)
            else:
                print(assets[key])
                assets[key].update(descriptions[val['classid']])
                items.append(self._format_inspect_url(assets[key]))
        for item in items:
            data = self._get_item_detail(item)
            if data.get('defindex') == defindex and data.get('float') == float and data.get('paintindex') == paintindex and data.get('paintseed') == paintseed:
                return True
        return False        

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
        return url.replace(f"%owner_steamid%", steamid).replace(f"%assetid%", assetid)

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
        

    def update_inventory(self):
        objs = []
        try:
            self.inventory.get('assets',None)
        except:
            self.data = {}
            return {}

        assets = {f"{mydict['assetid']}":mydict for mydict in self.inventory["assets"]}
        descriptions = {f"{mydict['classid']}":mydict for mydict in self.inventory["descriptions"]}

        existing_inventory = {item.assetid:item for item in InventoryItem.objects.filter(owner=self.user)}
        item_names = {name['market_hash_name'] for name in descriptions.values()}
        item_query =  Item.objects.in_bulk(item_names,field_name='market_hash_name')

        for key,val in assets.copy().items():
            if existing_inventory.get(key,None):
                continue

            assets[key].update(descriptions[val['classid']])

            if not self._is_marketable(assets[key]):
                continue

            url = self._format_inspect_url(assets[key])
            self._format_icon(assets[key])
            self._format_sticker(assets[key])
            item_detail =self._get_item_detail(url)      #TODO: GET sticker info and add it to sticker objs
            assets[key]['paintindex'] = item_detail.get('paintindex',0)
            assets[key]['paintseed'] = item_detail.get('paintseed',0)
            assets[key]['float'] = item_detail.get('floatvalue',0)
            assets[key]['defindex'] = item_detail.get('defindex',0)
            
            item = assets[key]
            inv =InventoryItem(
                owner=self.user,
                item=item_query.get(item['market_hash_name']),
                classid=item['classid'],
                instanceid=item['instanceid'],
                assetid=item['assetid'],
                tradable=item['tradable'],
                inspect_url=item['inspect_url'],
                float=item['float'],
                paintindex=item['paintindex'],
                paintseed=item['paintseed'],
                defindex=item['defindex']
                )
            objs.append(inv)
        objs = InventoryItem.objects.bulk_create(objs)

        for obj in objs:
            data_stickers = assets[obj.assetid]
            for sticker in data_stickers.get('stickers',[]):
                sticker = Item.objects.filter(type='Sticker',market_hash_name__icontains=sticker)
                if not sticker.exists():
                    continue
                addon= sticker.first()
                Addon.objects.create(item=addon,inventory=obj)
        # Delete non existing items in inventory in db // If its sold dont delete it from db
        excluded_items = InventoryItem.objects.filter(owner=self.user)
        excluded_items = excluded_items.exclude(assetid__in=[int(key) for key in assets.keys()])
        excluded_items.update(in_inventory=False)
        excluded_items = excluded_items.filter(item_state__in=[InventoryItem.ItemStateChoices.LIS,InventoryItem.ItemStateChoices.INV])
        excluded_items.delete()

class SteamTrade:
    """
        Package to check and verify steam trades from seller's end using seller's steam api key
    """
    GET_TRADE_OFFERS_URL = 'https://api.steampowered.com/IEconService/GetTradeOffers/v1/'
    GET_TRADE_OFFER_URL = 'https://api.steampowered.com/IEconService/GetTradeOffer/v1/'
    GET_TRADE_STATUS = 'https://api.steampowered.com/IEconService/GetTradeStatus/v1/'

    def __init__(self,api_key):
        self.get_trade_offers_pld = {'get_received_offers':'true','key':api_key}
        self.get_trade_offer_pld = {'key':api_key}
        self.get_trade_status_pld = {'key':api_key}
        self.api_key = api_key
    
    def check_trade_received(self,assetid,classid,instanceid)->dict:
        r = requests.get(self.GET_TRADE_OFFERS_URL,params=self.get_trade_offers_pld)
        resp = r.json()
        response = resp.get('response')

        if not response:
            return {'success':False} #TODO: Convert to raise exception
        trade_recv= response.get('trade_offers_received')
        if not trade_recv:
            return {'success':False} #TODO: Same as above
        for trade in trade_recv:
            items_to_receive = trade.get('items_to_receive')
            if not items_to_receive:
                continue
            elif len(items_to_receive) > 1:
                continue
            item = items_to_receive[0]
            if item.get('assetid') == assetid and item.get('classid') == classid and item.get('instanceid') == instanceid:
                return {'success':True,'tradeofferid':trade.get('tradeofferid')}
        return {'success':False}
    
    def check_trade_accepted(self,assetid,classid,instanceid,tradeofferid)->dict:
        get_trade_offer_pld = self.get_trade_offer_pld
        get_trade_offer_pld['tradeofferid'] = tradeofferid
        r = requests.get(self.GET_TRADE_OFFER_URL,params=get_trade_offer_pld)
        resp = r.json()

        response = resp.get('response')
        if not response:
            return {'success':False} #TODO: Same as above
        offer = response.get('offer')
        if not offer:
            return {'success':False} #TODO: Same as above
        items_to_receive = offer.get('items_to_receive')
        if len(items_to_receive) > 1:
            return {'success':False} #TODO: Same as above
        item = items_to_receive[0]
        if item.get('assetid') == assetid and item.get('classid') == classid and item.get('instanceid') == instanceid:
            if offer.get('trade_offer_state') == 3:
                return {'success':True,'tradeid':offer.get('tradeid')}
            else:
                return {'success':False,'tradeid':offer.get('tradeid'),'trade_offer_state':offer.get('trade_offer_state')}
    
    def check_trade_status(self,tradeid):
        get_trade_status_pld = self.get_trade_status_pld
        get_trade_status_pld['tradeid'] = tradeid
        r = requests.get(self.GET_TRADE_STATUS,params=get_trade_status_pld)
        resp = r.json()
        response = resp.get('response')
        if not response:
            return {'success':False} #TODO: Same as above
        trades = response.get('trades')
        if not trades:
            return {'success':False} #TODO: Same as above
        trade = trades[0]
        data = {'success':True,'status':trade.get('status'),'items':trade.get('assets_received')}
        return data