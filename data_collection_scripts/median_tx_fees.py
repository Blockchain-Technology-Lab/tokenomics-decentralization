import requests
import json
import tokenomics_decentralization.helper as hlp


def get_median_tx_fees(ledger, group_by):
    """
    Retrieves the median transaction fees for a ledger 
    (in its lowest denomination, e.g. satoshis for Bitcoin)
    from the Blockchair API
    and saves the data to a json file
    :param ledger: the ledger to retrieve the data for (e.g. bitcoin)
    :param group_by: the granularity of the data (date, week, month, year)
    """
    url = f"https://api.blockchair.com/{ledger}/transactions?a={group_by},median(fee)"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()        
    else:        
        print(f"Error: Failed to retrieve data from {url}")
        print("Error code:", response.status_code)
        print("Error message:", response.text)

def save_tx_fee_data_to_file(api_response, ledger, group_by):
    data = api_response["data"]
    data = {data[i][group_by]: int(data[i]["median(fee)"]) for i in range(len(data))}

    if ledger == "ethereum":  # For Ethereum, store the tx fees in Gwei
        data = {k: int(v / 1e9) for k, v in data.items()}

    data_dir = hlp.ROOT_DIR / "tx_fees" / ledger.replace("-", "_")
    data_dir.mkdir(parents=True, exist_ok=True)

    if group_by == "date":
        group_by = "day"
    with open(data_dir / f"median_tx_fees_{group_by}.json", "w") as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    ledgers = ["bitcoin", "bitcoin-cash", "dogecoin", "ethereum", "litecoin", "zcash"]
    granularities = ["date", "week", "month", "year"]
    for ledger in ledgers:
        print(f"Retrieving transaction fee data for {ledger}..")
        for granularity in granularities:
            tx_fee_data = get_median_tx_fees(ledger=ledger, group_by=granularity)
            save_tx_fee_data_to_file(api_response=tx_fee_data, ledger=ledger, group_by=granularity)
