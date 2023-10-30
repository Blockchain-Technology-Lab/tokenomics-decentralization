from tokenomics_decentralization.map import apply_mapping
from tokenomics_decentralization.analyze import analyze
from yaml import safe_load
import argparse
import pathlib
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

ROOT_DIR = pathlib.Path(__file__).resolve().parent


def main(ledgers, snapshots, force_compute, only_analyze, db_directories):
    if not only_analyze:
        for ledger in ledgers:
            for snapshot in snapshots:
                logging.info(f'Mapping {ledger} {snapshot}')
                apply_mapping(ledger, snapshot, db_directories)
    analyze(ledgers, snapshots, force_compute, db_directories)


if __name__ == '__main__':
    with open(ROOT_DIR / 'config.yaml') as f:
        config = safe_load(f)

    default_ledgers = config['default_ledgers']
    default_snapshot_dates = [f'{year}-01-01' for year in range(config['timeframe']['start_year'], config['timeframe']['end_year'] + 1)]

    db_directories = [pathlib.Path(db_dir).resolve() for db_dir in config['db_directories']]

    parser = argparse.ArgumentParser()
    parser.add_argument('--ledgers', nargs="*", type=str.lower, default=default_ledgers,
                        choices=[ledger for ledger in default_ledgers], help='The ledgers to collect data for.')
    parser.add_argument('--snapshots', nargs="*", type=str.lower, default=default_snapshot_dates,
                        help='The dates to collect data for.')
    parser.add_argument('--force-compute', action='store_true',
                        help='Flag to specify whether to query for project data regardless if the relevant data '
                             'already exist.')
    parser.add_argument('--only-analyze', action='store_true',
                        help='Flag to specify whether to only analyze existing data, if the database exists.')
    args = parser.parse_args()

    ledgers = args.ledgers
    snapshots = args.snapshots
    force_compute = args.force_compute
    only_analyze = args.only_analyze

    main(ledgers, snapshots, force_compute, only_analyze, db_directories)
