import requests
import json


def get_address_info():
    filename = 'tezos_address_aliases_all.json'
    try:
        with open(filename) as f:
            return json.load(f)
    except FileNotFoundError:
        # retrieve data from API      
        base_url = "https://api.tzkt.io/"
        accounts_endpoint = "v1/accounts/"
        count_endpoint = "count"

        total_accounts = requests.get(f'{base_url}{accounts_endpoint}{count_endpoint}').json()

        max_items = 10000
        offset = 0
        params = {"limit": max_items, "select": 'type,address,alias', "offset": offset}

        address_info = dict()

        while offset < total_accounts:
            accounts = requests.get(f'{base_url}{accounts_endpoint}', params=params).json()
            for account in accounts:
                if account["alias"]:
                    address_info[account["address"]] = {
                        "name": account["alias"],
                        "is_contract": account["type"] == 'contract',
                        "source": "https://api.tzkt.io/"
                        }
            offset += max_items
            params["offset"] = offset
            if offset % 100000 == 0:
                print(f'Processed {offset} accounts so far..')

        return address_info


def parse_aliases(address_info):
    aliases = {
        'Tezos Foundation': 'Tezos Foundation',
        'Foundation Baker': 'Tezos Foundation',
        'Foundation Delegator': 'Tezos Foundation'
    }

    single_aliases = ['Vested funds', 'Binance', 'Kraken', 'Coinbase', 'Huobi', 'OKEx', 'HitBTC', 'Bitfinex', 'BitMax',
                       'Bithumb', 'Bittrex', 'Upbit', 'KuCoin', 'Gate.io', 'Kolibri', 'Skull', 'Ageur', 'Vault', 
                       '3Route', 'DNAG', 'DOGAMI', 'Dashmaster', 'FXHASH', 'Gill', 'Hover Labs', 'Here and Now', 
                       'Lucid Mining', 'MATEUS', 'MATIC', 'PayTezos', 'Polychain Labs', 'QuipuSwap', 'Stake House',
                       'Tez Baker', 'Tezocracy', 'Tezos Capital Legacy', 'Ubinetic', 'Werenode EVSE', 'Youves',
                       'concierge', 'priyamistry', '8bidou', 'Chorus One', 'XTZMaster', 'Coinone']
    
    for alias in single_aliases:
        aliases[alias] = alias

    for value in address_info.values():
        for keyword in aliases:
            if value["name"].lower().startswith(keyword.lower()):
                value['extra_info'] = value["name"]
                value['name'] = aliases[keyword]
                break

    # save to json file
    with open('addresses/tezos.json', 'w') as f:
        json.dump(address_info, f, indent=4)
    return address_info


if __name__ == '__main__':
    address_info = get_address_info()
    parse_aliases(address_info)
