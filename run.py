from tokenomics_decentralization.map import apply_mapping
from tokenomics_decentralization.analyze import analyze
from tokenomics_decentralization.plot import plot
import tokenomics_decentralization.helper as hlp
import argparse
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def main(ledgers, snapshot_dates, force_analyze, no_clustering):
    for ledger in ledgers:
        for snapshot in snapshot_dates:
            apply_mapping(ledger, snapshot)
    analyze(ledgers, snapshot_dates, force_analyze, no_clustering)
    plot()


if __name__ == '__main__':
    config = hlp.get_config_data()

    default_snapshot_dates = hlp.get_default_snapshots()

    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot_dates', nargs="*", type=hlp.valid_date, default=default_snapshot_dates,
                        help='The dates to to analyze. Any number of dates can be specified, in the format "YYYY-MM-DD", '
                        '"YYYY-MM" or "YYYY". If two dates are given and the --granularity argument is '
                        'not "none", then the dates are interpreted as the beginning and end of a time period, and the '
                        'granularity is used to determine which snapshots to analyze in between (e.g. every month).')
    args = parser.parse_args()

    snapshot_dates = args.snapshot_dates

    ledgers = hlp.get_default_ledgers()

    force_analyze = config['force_analyze']
    no_clustering = config['no_clustering']

    granularity = config['granularity']
    if granularity in ['day', 'week', 'month', 'year'] and len(snapshot_dates) > 1:
        start_date, end_date = hlp.get_date_beginning(snapshot_dates[0]), hlp.get_date_end(snapshot_dates[-1])
        snapshot_dates = hlp.get_dates_between(start_date, end_date, granularity)
    else:
        snapshot_dates = [hlp.get_date_string_from_object(hlp.get_date_beginning(date)) for date in snapshot_dates]

    if not hlp.OUTPUT_DIR.is_dir():
        hlp.OUTPUT_DIR.mkdir()

    main(ledgers, snapshot_dates, force_analyze, no_clustering)
