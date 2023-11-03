import requests
import json


def get_address_aliases():
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
        params = {"limit": max_items, "select": 'id,type,address,alias,balance', "offset": offset}

        address_aliases = dict()

        while offset < total_accounts:
            accounts = requests.get(f'{base_url}{accounts_endpoint}', params=params).json()
            for account in accounts:
                if account["alias"]:
                    address_aliases[account["address"]] = {"name": account["alias"], "source": "https://api.tzkt.io/"}
            offset += max_items
            params["offset"] = offset
            print(f'Processed {offset} accounts so far..')

        return address_aliases


def parse_aliases(address_aliases):    
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

    for value in address_aliases.values():
        for keyword in aliases:
            if value["name"].lower().startswith(keyword.lower()):
                value['extra_info'] = value["name"]
                value['name'] = aliases[keyword]
                break

    # save to json file
    with open('addresses/tezos.json', 'w') as f:
        json.dump(address_aliases, f, indent=4)
    return address_aliases

if __name__ == '__main__':
    address_aliases = get_address_aliases()
    parse_aliases(address_aliases)
