import json
import requests
import tokenomics_decentralization.helper as hlp
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

api_url = 'https://api.xrpscan.com/api/v1/names/well-known'
response = requests.get(api_url)
data = response.json()

data_dir = hlp.MAPPING_INFO_DIR / "addresses"
logging.info(f'Saving XRPL address info to {data_dir / "xrpl.jsonl"}')

with open(data_dir / 'xrpl.jsonl', 'w') as outfile:
    for entry in data:
        # rename account to address for consistency
        if 'account' in entry:
            entry['address'] = entry.pop('account')
        # add source field
        entry['source'] = 'https://api.xrpscan.com'
        json_line = json.dumps(entry)
        outfile.write(json_line + '\n')
