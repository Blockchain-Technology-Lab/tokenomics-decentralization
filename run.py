from tokenomics_decentralization.map import apply_mapping
from tokenomics_decentralization.analyze import analyze
from plot import plot
import tokenomics_decentralization.helper as hlp
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def main(ledgers, snapshot_dates):
    for ledger in ledgers:
        for snapshot in snapshot_dates:
            apply_mapping(ledger, snapshot)

    analyze(ledgers, snapshot_dates)

    if hlp.get_plot_flag():
        plot()


if __name__ == '__main__':
    ledgers = hlp.get_ledgers()

    snapshot_dates = hlp.get_snapshot_dates()

    granularity = hlp.get_granularity()
    if granularity in ['day', 'week', 'month', 'year']:
        start_date, end_date = hlp.get_date_beginning(snapshot_dates[0]), hlp.get_date_end(snapshot_dates[-1])
        snapshot_dates = hlp.get_dates_between(start_date, end_date, granularity)
    else:
        snapshot_dates = [hlp.get_date_string_from_date(hlp.get_date_beginning(date)) for date in snapshot_dates]

    output_dir = hlp.get_output_directories()[0]
    if not output_dir.is_dir():
        output_dir.mkdir()

    main(ledgers, snapshot_dates)
