from tokenomics_decentralization.map import apply_mapping
from tokenomics_decentralization.analyze import analyze
from tokenomics_decentralization.plot import plot
import tokenomics_decentralization.helper as hlp
from yaml import safe_load
import argparse
import pathlib
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

ROOT_DIR = pathlib.Path(__file__).resolve().parent


def main(ledgers, snapshots, force_compute, only_analyze, db_directories, no_clustering):
    if not only_analyze:
        for ledger in ledgers:
            for snapshot in snapshots:
                logging.info(f'Mapping {ledger} {snapshot}')
                apply_mapping(ledger, snapshot, db_directories)
    analyze(ledgers, snapshots, force_compute, db_directories, no_clustering)
    plot()


if __name__ == '__main__':
    with open(ROOT_DIR / 'config.yaml') as f:
        config = safe_load(f)

    default_ledgers = hlp.get_default_ledgers()
    start_date, end_date = hlp.get_default_start_end_dates()
    default_snapshot_dates = [f'{year}-01-01' for year in range(int(start_date[:4]), int(end_date[:4]) + 1)]

    db_directories = [pathlib.Path(db_dir).resolve() for db_dir in config['db_directories']]

    parser = argparse.ArgumentParser()
    parser.add_argument('--ledgers', nargs="*", type=str.lower, default=default_ledgers,
                        choices=[ledger for ledger in default_ledgers], help='The ledgers to analyze')
    parser.add_argument('--snapshot_dates', nargs="*", type=hlp.valid_date, 
                        default=default_snapshot_dates, help='The dates to to analyze.')
    parser.add_argument('--force-compute', action='store_true',
                        help='Flag to specify whether to query for project data regardless if the relevant data '
                        'already exist.')
    parser.add_argument('--only-analyze', action='store_true',
                        help='Flag to specify whether to only analyze existing data, if the database exists.')
    parser.add_argument('--no-clustering', action='store_true',
                        help='Flag to specify whether to not perform any address clustering.')
    args = parser.parse_args()

    ledgers = args.ledgers
    snapshots = args.snapshot_dates
    force_compute = args.force_compute
    only_analyze = args.only_analyze
    no_clustering = args.no_clustering

    main(ledgers, snapshots, force_compute, only_analyze, db_directories, no_clustering)
