import csv
import os.path
import tokenomics_decentralization.helper as hlp
import tokenomics_decentralization.db_helper as db_hlp
from collections import defaultdict
from tokenomics_decentralization.metrics import (compute_hhi, compute_tau, compute_gini, compute_shannon_entropy,
                                                 compute_total_entities, compute_max_power_ratio, compute_theil_index)
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def analyze_snapshot(entries):
    """
    Applies thresholding based on the config parameters and then applies
    the metrics on the given entries.
    :param entries: a list of tuples (balance, ), where balance is an integer, in descending order
    :returns: a dictionary where the key is the name of the computed metric prefixed with the applied thresholds and the value is a number
    """
    compute_functions = {
        'hhi': compute_hhi,
        'shannon_entropy': compute_shannon_entropy,
        'gini': compute_gini,
        'total_entities': compute_total_entities,
        'mpr': compute_max_power_ratio,
        'theil': compute_theil_index
    }
    for threshold in hlp.get_tau_thresholds():
        compute_functions[f'tau={threshold}'] = compute_tau

    top_limit_type = hlp.get_top_limit_type()
    top_limit_value = hlp.get_top_limit_value()
    if top_limit_value > 0:
        if top_limit_type == 'percentage':
            total_entities = compute_functions['total_entities'](entries, -1)
            top_limit_percentage_value = int(total_entities * top_limit_value)
            entries = entries[:top_limit_percentage_value]
        elif top_limit_type == 'absolute':
            entries = entries[:top_limit_value]

    circulation = hlp.get_circulation_from_entries(entries)

    metrics_results = {}
    for default_metric_name in hlp.get_metrics():
        flagged_metric = default_metric_name
        if not hlp.get_clustering_flag():
            flagged_metric = 'non-clustered ' + flagged_metric
        if hlp.get_exclude_contracts_flag():
            flagged_metric = 'exclude_contracts ' + flagged_metric
        if hlp.get_exclude_below_fees_flag():
            flagged_metric = 'exclude_below_fees ' + flagged_metric
        if hlp.get_exclude_below_usd_cent_flag():
            flagged_metric = 'exclude_below_usd_cent ' + flagged_metric
        if top_limit_value > 0:
            flagged_metric = f'top-{top_limit_value}_{top_limit_type} ' + flagged_metric

        if 'tau' in default_metric_name:
            threshold = float(default_metric_name.split('=')[1])
            metric_value = compute_functions[default_metric_name](entries, circulation, threshold)
        else:
            metric_value = compute_functions[default_metric_name](entries, circulation)

        if any(['tau' in default_metric_name, 'total_entities' in default_metric_name]):
            metric_value = int(metric_value)

        metrics_results[flagged_metric] = metric_value

    return metrics_results


def get_entries(ledger, date, filename):
    """
    Collects the balance entries and applies the address mapping on them.
    Also applies filters on them based on the config flags.
    Finally orders the entries in descending order.
    :param ledger: a string of a ledger's name
    :param date: a string in YYYY-MM-DD format of the snapshot that is retrieved
    :param filename: the path of the file that stores the snapshot's raw data
    :returns: a list of tuples (balance, ), where balance is an integer, in descending order
    """
    exclude_below_fees_flag = hlp.get_exclude_below_fees_flag()
    exclude_below_usd_cent_flag = hlp.get_exclude_below_usd_cent_flag()

    median_tx_fee = hlp.get_median_tx_fee(ledger=ledger, date=date) \
        if exclude_below_fees_flag else 0
    usd_cent_equivalent = hlp.get_usd_cent_equivalent(ledger=ledger, date=date) \
        if exclude_below_usd_cent_flag else 0
    balance_threshold = max(median_tx_fee, usd_cent_equivalent)

    conn = db_hlp.get_connector(db_hlp.get_db_filename(ledger))
    special_addresses = hlp.get_special_addresses(ledger)

    with open(filename) as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        clustered_balances = defaultdict(int)
        for line in csv_reader:
            address, balance = line[0], int(line[-1])
            if address in special_addresses:
                continue
            entity = db_hlp.get_address_entity(conn, address)
            clustered_balances[entity] += balance

    entries = []
    while clustered_balances:
        item = clustered_balances.popitem()
        if item[1] > balance_threshold:
            entries.append((item[1], ))
    entries.sort(key=lambda x: x[0], reverse=True)

    return entries


def analyze(ledgers, snapshot_dates):
    """
    Executes the analysis of the given ledgers for the snapshot dates and writes the output
    to csv files.
    :param ledgers: a list of ledger names
    :param snapshot_dates: a list of strings in YYYY-MM-DD format
    """
    output_rows = []
    for ledger in ledgers:
        logging.info(f'[*] {ledger} - Analyzing')
        for date in snapshot_dates:
            logging.info(f'[*] {ledger} - {date}')

            input_filename = None
            input_paths = [input_dir / f'{ledger}_{date}_raw_data.csv' for input_dir in hlp.get_input_directories()]
            for filename in input_paths:
                if os.path.isfile(filename):
                    input_filename = filename
                    break
            if not input_filename:
                logging.error(f'{ledger} input data for {date} do not exist')
                continue

            entries = get_entries(ledger, date, filename)
            metrics_values = analyze_snapshot(entries)
            del entries

            output_rows.append(hlp.get_output_row(ledger, date, metrics_values))
            for metric, value in metrics_values.items():
                logging.info(f'{metric}: {value}')

    hlp.write_csv_output(output_rows)
