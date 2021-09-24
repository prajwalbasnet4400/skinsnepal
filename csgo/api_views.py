from csgo.models import Listing
from django.http import JsonResponse
import requests


def get_price(request,*args, **kwargs):                                             # Cache this, max: 1000 request per hour
    market_hash_name = kwargs.get('market_hash_name',None)
    if not market_hash_name:
        return JsonResponse({'success':False,'error':'required param market_hash_name'})
    
    url = """https://csgobackpack.net/api/GetItemPrice/?currency=NPR&id={market_hash_name}"""
    url = url.format(market_hash_name=market_hash_name)
    r = requests.get(url)
    if r.status_code != 200:
        return JsonResponse({'success':False,'error':f'API {r.status_code}'})
    
    data = r.json()
    min_listed = Listing.objects.filter(item__market_hash_name__icontains=market_hash_name).order_by('price').values('price').first()
    data.update({'min_listed':min_listed.get('price')})
    return JsonResponse(data)    
