"""
    This script can be used to run queries on BigQuery for any number of blockchains, and save the results in the input
    directory of the project.
    The relevant queries must be stored in a file named 'queries.yaml' in the root directory of the project.

    Attention! Before running this script, you need to generate service account credentials from Google, as described
    here (https://developers.google.com/workspace/guides/create-credentials#service-account) and save your key in the
    root directory of the project under the name 'google-service-account-key-0.json'. Any additional keys should be
    named 'google-service-account-key-1.json', 'google-service-account-key-2.json', etc.
"""
import google.cloud.bigquery as bq
import csv
from yaml import safe_load
import logging
import argparse
import tokenomics_decentralization.helper as hlp


def collect_data(ledgers, snapshot_dates, force_query):
    input_dir = hlp.INPUT_DIR
    root_dir = hlp.ROOT_DIR
    if not input_dir.is_dir():
        input_dir.mkdir()

    with open(root_dir / "queries.yaml") as f:
        queries = safe_load(f)

    i = 0
    all_quota_exceeded = False

    for ledger in ledgers:
        for date in snapshot_dates:
            if all_quota_exceeded:
                break
            file = input_dir / f'{ledger}_{date}_raw_data.csv'
            if not force_query and file.is_file():
                logging.info(f'{ledger} data for {date} already exists locally. '
                             f'For querying {ledger} anyway please run the script using the flag --force-query')
                continue
            logging.info(f"Querying {ledger} at snapshot {date}..")

            rows = None
            query = (queries[ledger]).replace('{{timestamp}}', date)

            while True:
                try:
                    client = bq.Client.from_service_account_json(json_credentials_path=root_dir / f"google-service-account-key-{i}.json")
                except FileNotFoundError:
                    logging.info(f'Exhausted all {i} service account keys. Aborting..')
                    all_quota_exceeded = True
                    break
                query_job = client.query(query)
                try:
                    rows = query_job.result()
                    logging.info(f'Done querying {ledger}')
                    break
                except Exception as e:
                    if 'Quota exceeded' in repr(e):
                        i += 1
                        logging.info(f'Quota exceeded with service account key {i - 1}, trying to use key {i}..')
                        continue
                    else:
                        logging.info(f'{ledger} query failed, please make sure it is properly defined.')
                        logging.info(f'The following exception was raised: {repr(e)}')
                        break

            if rows:
                logging.info(f"Writing {ledger} data to file..")
                with open(file, 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow([field.name for field in rows.schema])
                    writer.writerows(rows)
                logging.info(f'Done writing {ledger} data to file.\n')


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

    with open(hlp.ROOT_DIR / "config.yaml") as f:
        config = safe_load(f)
    default_ledgers = hlp.get_default_ledgers()
    default_snapshot_dates = hlp.get_default_snapshots()

    parser = argparse.ArgumentParser()
    parser.add_argument('--ledgers', nargs="*", type=str.lower, default=default_ledgers,
                        choices=[ledger for ledger in default_ledgers], help='The ledgers to collect data for.')
    parser.add_argument('--snapshot_dates', nargs="*", type=hlp.valid_date, default=default_snapshot_dates,
                        help='The dates to collect data for.')
    parser.add_argument('--force-query', action='store_true',
                        help='Flag to specify whether to query for project data regardless if the relevant data '
                             'already exist.')
    args = parser.parse_args()
    collect_data(ledgers=args.ledgers, snapshot_dates=args.snapshot_dates, force_query=args.force_query)
