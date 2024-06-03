"""
    This script can be used to run queries on BigQuery for any number of blockchains,
    and save the results in the input directory of the project.
    The relevant queries must be stored in a file named 'queries.yaml'
    in the data_collection_scripts directory of the project.

    Attention! Before running this script, you need to generate service account credentials from Google, as described
    here (https://developers.google.com/workspace/guides/create-credentials#service-account) and save your key in the
    data_collection_scripts directory of the project under the name 'google-service-account-key-0.json'. Any additional
    keys should be named 'google-service-account-key-1.json', 'google-service-account-key-2.json', etc.
"""
import json
import google.cloud.bigquery as bq
import csv
from yaml import safe_load
import logging
import argparse
import tokenomics_decentralization.helper as hlp
from datetime import datetime


def collect_data(ledger_snapshot_dates, force_query):
    input_dir = hlp.get_input_directories()[0]
    root_dir = hlp.ROOT_DIR
    if not input_dir.is_dir():
        input_dir.mkdir()

    with open(root_dir / "data_collection_scripts/queries.yaml") as f:
        queries = safe_load(f)

    i = 0
    all_quota_exceeded = False
    ledger_last_updates = dict.fromkeys(ledger_snapshot_dates.keys())

    for ledger, snapshot_dates in ledger_snapshot_dates.items():
        for date in snapshot_dates:
            if all_quota_exceeded:
                return ledger_last_updates
            file = input_dir / f'{ledger}_{date}_raw_data.csv'
            if not force_query and file.is_file():
                logging.info(f'{ledger} data for {date} already exists locally. '
                             f'For querying {ledger} anyway please run the script using the flag --force-query')
                ledger_last_updates[ledger] = date
                continue
            logging.info(f"Querying {ledger} at snapshot {date}..")

            rows = None
            query = (queries[ledger]).replace('{{timestamp}}', date)

            while True:
                try:
                    client = bq.Client.from_service_account_json(json_credentials_path=root_dir / f"data_collection_scripts/google-service-account-key-{i}.json")
                except FileNotFoundError:
                    logging.info(f'Exhausted all {i} service account keys. Aborting..')
                    all_quota_exceeded = True
                    return ledger_last_updates
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
                ledger_last_updates[ledger] = date
    return ledger_last_updates


def get_from_dates(granularity):
    """
    Get the dates from which to start querying for each ledger, which corresponds to the last updated date + the granularity
    (e.g. the month following the last update if granularity is 'month').
    :param granularity: The granularity of the data collection. Can be 'day', 'week', 'month', or 'year'.
    :return: A dictionary with ledgers as keys and the corresponding start dates as values.
    """
    with open(hlp.ROOT_DIR / "data_collection_scripts/last_update.json") as f:
        last_update = json.load(f)
    from_dates = {}
    for ledger in last_update:
        from_dates[ledger] = hlp.increment_date(date=hlp.get_date_beginning(last_update[ledger]), by=granularity)
    return from_dates


def update_last_update(ledger_last_updates):
    """
    Update the last_update.json file with the last date for which data was collected for each ledger.
    :param ledger_last_updates: A dictionary with the ledgers for which data was collected and the last date for which data was collected for each of them.
    """
    filepath = hlp.ROOT_DIR / "data_collection_scripts/last_update.json"
    with open(filepath) as f:
        last_update = json.load(f)
    for ledger, date in ledger_last_updates.items():
        if date is not None:
            last_update[ledger] = date
    with open(filepath, 'w') as f:
        json.dump(last_update, f)


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

    default_ledgers = hlp.get_ledgers()

    parser = argparse.ArgumentParser()
    parser.add_argument('--ledgers', nargs="*", type=str.lower, default=default_ledgers,
                        choices=[ledger for ledger in default_ledgers], help='The ledgers to collect data for.')
    parser.add_argument('--to_date', type=hlp.valid_date,
                        default=datetime.today().strftime('%Y-%m-%d'),
                        help='The date until which to get data for (YYYY-MM-DD format). Defaults to today.')
    parser.add_argument('--force-query', action='store_true',
                        help='Flag to specify whether to query for project data regardless if the relevant data '
                             'already exist.')
    args = parser.parse_args()

    to_date = hlp.get_date_beginning(args.to_date)
    ledgers = args.ledgers
    granularity = hlp.get_granularity()
    if granularity is None:
        ledger_snapshot_dates = {ledger: [hlp.get_date_string_from_date(to_date)] for ledger in ledgers}
    else:
        ledger_from_dates = get_from_dates(granularity=granularity)
        ledger_snapshot_dates = {ledger: hlp.get_dates_between(ledger_from_dates[ledger], to_date, granularity) for ledger in ledgers}
    ledger_last_updates = collect_data(ledger_snapshot_dates=ledger_snapshot_dates, force_query=args.force_query)
    update_last_update(ledger_last_updates=ledger_last_updates)
