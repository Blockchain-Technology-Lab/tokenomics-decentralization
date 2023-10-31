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
import logging
import argparse

ROOT_DIR = pathlib.Path(__file__).resolve().parent
INPUT_DIR = ROOT_DIR / 'input'


def collect_data(ledgers, snapshot_dates, force_query):
    if not INPUT_DIR.is_dir():
        INPUT_DIR.mkdir()

    with open(ROOT_DIR / "queries.yaml") as f:
        queries = safe_load(f)

    client = bq.Client.from_service_account_json(json_credentials_path=ROOT_DIR / "google-service-account-key.json")

    for ledger in ledgers:
        for date in snapshot_dates:
            file = INPUT_DIR / f'{ledger}_{date}_raw_data.csv'
            if not force_query and file.is_file():
                logging.info(f'{ledger} data for {date} already exists locally. '
                             f'For querying {ledger} anyway please run the script using the flag --force-query')
                continue
            logging.info(f"Querying {ledger} at snapshot {date}..")
            query = (queries[ledger]).replace('{{timestamp}}', date)
            query_job = client.query(query)
            try:
                rows = query_job.result()
                logging.info(f'Done querying {ledger}')
            except Exception as e:
                logging.info(f'{ledger} query failed, please make sure it is properly defined.')
                logging.info(f'The following exception was raised: {repr(e)}')
                continue

            logging.info(f"Writing {ledger} data to file..")
            with open(file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow([field.name for field in rows.schema])
                writer.writerows(rows)
            logging.info(f'Done writing {ledger} data to file.\n')


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

    default_ledgers = ['bitcoin', 'cardano', 'ethereum', 'dogecoin']
    start_year, end_year = 2018, 2023
    default_snapshot_dates = [f'{year}-01-01' for year in range(start_year, end_year + 1)]

    parser = argparse.ArgumentParser()
    parser.add_argument('--ledgers', nargs="*", type=str.lower, default=default_ledgers,
                        choices=[ledger for ledger in default_ledgers], help='The ledgers to collect data for.')
    parser.add_argument('--snapshot_dates', nargs="*", type=str.lower, default=default_snapshot_dates,
                        help='The dates to collect data for.')
    parser.add_argument('--force-query', action='store_true',
                        help='Flag to specify whether to query for project data regardless if the relevant data '
                             'already exist.')
    args = parser.parse_args()
    collect_data(ledgers=args.ledgers, snapshot_dates=args.snapshot_dates, force_query=args.force_query)
