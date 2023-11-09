from tokenomics_decentralization.map import apply_mapping
from tokenomics_decentralization.analyze import analyze
from tokenomics_decentralization.plot import plot
import tokenomics_decentralization.helper as hlp
import argparse
import pathlib
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def main(ledgers, snapshot_dates, force_compute, force_map, only_analyze, db_directories, no_clustering):
    if not only_analyze:
        for ledger in ledgers:
            for snapshot in snapshot_dates:
                if not (hlp.OUTPUT_DIR / f'{ledger}_{snapshot}.db').is_file() or force_map:
                    apply_mapping(ledger, snapshot, db_directories)
    analyze(ledgers, snapshot_dates, force_compute, db_directories, no_clustering)
    plot()


if __name__ == '__main__':
    config = hlp.get_config_data()

    default_ledgers = hlp.get_default_ledgers()
    default_snapshot_dates = hlp.get_default_snapshots()

    db_directories = [pathlib.Path(db_dir).resolve() for db_dir in config['db_directories']]

    parser = argparse.ArgumentParser()
    parser.add_argument('--ledgers', nargs="*", type=str.lower, default=default_ledgers,
                        choices=[ledger for ledger in default_ledgers], help='The ledgers to analyze')
    parser.add_argument('--snapshot_dates', nargs="*", type=hlp.valid_date, default=default_snapshot_dates,
                        help='The dates to to analyze. Any number of dates can be specified, in the format "YYYY-MM-DD", '
                        '"YYYY-MM" or "YYYY". If two dates are given and the --granularity argument is '
                        'not "none", then the dates are interpreted as the beginning and end of a time period, and the '
                        'granularity is used to determine which snapshots to analyze in between (e.g. every month).')
    args = parser.parse_args()

    ledgers = args.ledgers
    snapshot_dates = args.snapshot_dates

    force_compute = config['force_compute']
    force_map = config['force_map']
    only_analyze = config['only_analyze']
    no_clustering = config['no_clustering']

    granularity = config['granularity']
    if len(snapshot_dates) == 2:
        start_date, end_date = hlp.get_date_beginning(snapshot_dates[0]), hlp.get_date_end(snapshot_dates[-1])
        snapshot_dates = hlp.get_dates_between(start_date, end_date, granularity)
    else:
        snapshot_dates = [hlp.get_date_string_from_object(hlp.get_date_beginning(date)) for date in snapshot_dates]

    if not hlp.OUTPUT_DIR.is_dir():
        hlp.OUTPUT_DIR.mkdir()

    main(ledgers, snapshot_dates, force_compute, force_map, only_analyze, db_directories, no_clustering)
