"""
    This script can be used to run queries on BigQuery for any number of blockchains, and save the results in the input
    directory of the project.
    The relevant queries must be stored in a file named 'queries.yaml' in the root directory of the project.

    Attention! Before running this script, you need to generate service account credentials from Google, as described
    here (https://developers.google.com/workspace/guides/create-credentials#service-account) and save your key in the
    root directory of the project under the name 'google-service-account-key.json'
"""
import google.cloud.bigquery as bq
import csv
from yaml import safe_load
import pathlib
from time import time

ROOT_DIR = pathlib.Path(__file__).resolve().parent
INPUT_DIR = ROOT_DIR / 'input'

if not INPUT_DIR.is_dir():
    INPUT_DIR.mkdir()

with open(ROOT_DIR / "queries.yaml") as f:
    queries = safe_load(f)

client = bq.Client.from_service_account_json(json_credentials_path=ROOT_DIR / "google-service-account-key.json")

force_query = False
for ledger in queries.keys():
    filename = f'{ledger}_raw_data.csv'
    file = INPUT_DIR / filename
    if not force_query and file.is_file():
        continue
    print(f"Querying {ledger}..")
    start = time()
    QUERY = (queries[ledger])
    query_job = client.query(QUERY)
    try:
        rows = query_job.result()
        print(f'Done querying {ledger} (took about {round(time() - start)} seconds)')
    except Exception as e:
        print(f'{ledger} query failed, please make sure it is properly defined.')
        print(f'The following exception was raised: {repr(e)}')
        continue

    print(f"Writing {ledger} data to file..")
    start = time()
    with open(file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow([field.name for field in rows.schema])
        writer.writerows(rows)
    print(f'Done writing {ledger} results (took about {round(time() - start)} seconds)')
    print(50 * '-')
