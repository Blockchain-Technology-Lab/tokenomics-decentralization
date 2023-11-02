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

        # save to json file
        with open(filename, 'w') as f:
            json.dump(address_aliases, f, indent=4)
        return address_aliases


def parse_aliases(address_aliases):
    keywords = [
        'Foundation Baker',  # Tezos Foundation
        'Foundation Delegator',  # Tezos Foundation
        'Vested funds',
        'Binance',  # exchange
        'Kraken',  # exchange 
        'Coinbase',  # exchange 
        'Huobi',  # exchange 
        'OKEx',  # exchange 
        'HitBTC',  # exchange 
        'Bitfinex',  # exchange 
        'BitMax',  # exchange 
        'Bithumb',  # exchange 
        'Bittrex',  # exchange 
        'Upbit',  # exchange
        'KuCoin',  # exchange
        'Gate.io',  # exchange
        'Kolibri',  # DeFi
        'Skull',  # DeFi
        'Ageur',  # DeFi
        'Vault',
        '3Route',
        'DNAG',
        'DOGAMI',
        'Dashmaster',
        'FXHASH',
        'Gill',
        'Hover Labs',
        'Here and Now',
        'Lucid Mining',
        'MATEUS',
        'MATIC',   
        'PayTezos',
        'Polychain Labs',
        'QuipuSwap',
        'Stake House',
        'Tez Baker',
        'Tezocracy',
        'Tezos Capital Legacy',
        'Ubinetic',
        'Werenode EVSE',
        'Youves',
        'concierge',
        'priyamistry',
        '8bidou'
        ]
    for address, alias in address_aliases.items():
        for keyword in keywords:
            if keyword.lower() in alias["name"].lower():
                alias['name'] = keyword
                break

    # save to json file
    with open('tezos_address_aliases_clustered.json', 'w') as f:
        json.dump(address_aliases, f, indent=4)
    return address_aliases

if __name__ == '__main__':
    address_aliases = get_address_aliases()
    parse_aliases(address_aliases)
