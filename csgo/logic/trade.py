import requests

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