import requests


def get_csgo_items():
    item_list = []
    data = requests.get(
        'https://csgobackpack.net/api/GetItemsList/v2/?no_prices=True').json()
    if not data.get('success'):
        return None
    data = data['items_list']
    for value in data.values():
        market_hash_name = value.get('name')
        type = value.get('type', None)
        icon_url = value.get('icon_url')
        icon_url_large = value.get('icon_url', None)

        sticker = value.get('sticker')
        weapon_type = value.get('weapon_type')
        exterior = value.get('exterior')
        rarity = value.get('rarity')
        rarity_color = value.get('rarity_color')
        first_sale_date = value.get('first_sale_date')
        stattrak = value.get('stattrak')
        souvenir = value.get('souvenir', None)
        tournament = value.get('tournament', None)

        if type == 'Weapon':
            if weapon_type != 'Knife':
                sub_type = value.get('gun_type')
                name = market_hash_name.split('|')
                name = name[-1]
                name = name.split('(')
                name = name[0]
            else:
                sub_type = value.get('knife_type')
                name = market_hash_name.split('|')
                name = name[-1]
                name = name.split('(')
            # Exterior missing fix
            if not exterior:
                exterior = name[-1]
                exterior = exterior.rstrip(')')
                name = name[0]

        elif type == None and sticker == True:
            type = 'Sticker'
            sub_type = None
            rarity = value.get('rarity')
            rarity_color = value.get('rarity_color')
            first_sale_date = value.get('first_sale_date')
            name = market_hash_name.split('|')
            if len(name) == 3:
                name = f'{name[-2]} | {name[-1]}'
            else:
                name = name[-1]

        elif type == 'Gloves':
            sub_type = None
            name = market_hash_name.split('(')
            exterior = name[-1]
            exterior = exterior.rstrip(')')
            name = name[0]
        else:
            continue
        item = {'name': name, 'market_hash_name': market_hash_name, 'icon_url': icon_url, 'icon_url_large': icon_url_large,
                'type': type, 'weapon_type': weapon_type, 'sub_type': sub_type, 'exterior': exterior, 'exterior': exterior,
                'rarity': rarity, 'rarity_color': rarity_color, 'souvenir': souvenir, 'tournament': tournament, 'stattrak': stattrak}
        item_list.append(item)
    return item_list


def get_item_price(name: str) -> dict:
    params = {
        'market_hash_name': name,
        'currency': 1,
        'appid': 730
    }
    url = f'https://steamcommunity.com/market/priceoverview/'
    r = requests.get(url, params=params)
    response = r.json()
    response['name'] = name
    return response