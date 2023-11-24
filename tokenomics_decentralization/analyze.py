from tokenomics_decentralization.schema import get_connector
from tokenomics_decentralization.metrics import compute_hhi, compute_tau, compute_gini, compute_shannon_entropy, compute_total_entities, compute_max_power_ratio
import tokenomics_decentralization.helper as hlp
import tokenomics_decentralization.db_helper as db_hlp
import os
import logging
import csv

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def analyze_snapshot(conn, ledger, snapshot):
    force_analyze = hlp.get_force_analyze_flag()
    no_clustering = hlp.get_no_clustering_flag()
    top_limit_type = hlp.get_top_limit_type()
    top_limit_value = hlp.get_top_limit_value()
    exclude_contract_addresses_flag = hlp.get_exclude_contracts_flag()
    exclude_below_fees_flag = hlp.get_exclude_below_fees_flag()

    snapshot_info = db_hlp.get_snapshot_info(conn, ledger, snapshot)
    snapshot_id = snapshot_info[0]
    circulation = int(float(snapshot_info[3]))

    snapshot_date = snapshot_info[1]
    median_tx_fee = hlp.get_median_tx_fee(ledger=ledger, date=snapshot_date) if hlp.get_exclude_below_fees_flag() else -1

    compute_functions = {
        'hhi': compute_hhi,
        'shannon entropy': compute_shannon_entropy,
        'gini': compute_gini,
        'total entities': compute_total_entities,
        'mpr': compute_max_power_ratio,
    }
    for threshold in hlp.get_tau_thresholds():
        compute_functions[f'tau={threshold}'] = compute_tau

    metric_names = hlp.get_metrics()

    entries = None
    metrics_results = {}
    for default_metric_name in metric_names:
        flagged_metric = default_metric_name
        if no_clustering:
            flagged_metric = 'non-clustered ' + flagged_metric
        if exclude_contract_addresses_flag:
            flagged_metric = 'exclude_contracts ' + flagged_metric
        if exclude_below_fees_flag:
            flagged_metric = 'exclude_below_fees ' + flagged_metric
        if top_limit_value > 0:
            flagged_metric = f'top-{top_limit_value}_{top_limit_type} ' + flagged_metric

        val = db_hlp.get_metric_value(conn, ledger, snapshot, flagged_metric)
        if val and not force_analyze:
            metric_value = val[0]
        else:
            if not entries:
                if no_clustering:
                    entries = db_hlp.get_non_clustered_balance_entries(conn, snapshot_id, ledger, balance_threshold=median_tx_fee)
                else:
                    entries = db_hlp.get_balance_entries(conn, snapshot_id, ledger, balance_threshold=median_tx_fee)

                if top_limit_value > 0:
                    if top_limit_type == 'percentage':
                        total_entities = compute_functions['total entities'](entries, circulation)
                        top_limit_percentage_value = int(total_entities * top_limit_value)
                        entries = entries[:top_limit_percentage_value]
                    elif top_limit_type == 'absolute':
                        entries = entries[:top_limit_value]

                    circulation = hlp.get_circulation_from_entries(entries)

            logging.info(f'Computing {flagged_metric}')
            if 'tau' in default_metric_name:
                threshold = float(default_metric_name.split('=')[1])
                metric_value = compute_functions[default_metric_name](entries, circulation, threshold)[0]
            else:
                metric_value = compute_functions[default_metric_name](entries, circulation)

            db_hlp.insert_metric(conn, ledger, snapshot, flagged_metric, metric_value)

            db_hlp.commit_database(conn)

        if any(['tau' in default_metric_name, 'total entities' in default_metric_name]):
            metric_value = int(metric_value)

        metrics_results[flagged_metric] = metric_value

    return metrics_results


def get_output_row(ledger, date, metrics):
    no_clustering = hlp.get_no_clustering_flag()
    exclude_contract_addresses_flag = hlp.get_exclude_contracts_flag()
    exclude_below_fees_flag = hlp.get_exclude_below_fees_flag()
    top_limit_type = hlp.get_top_limit_type()
    top_limit_value = hlp.get_top_limit_value()

    csv_row = [ledger, date, no_clustering, exclude_contract_addresses_flag, top_limit_type, top_limit_value]

    for metric_name in hlp.get_metrics():
        val = metric_name
        if no_clustering:
            val = 'non-clustered ' + val
        if exclude_contract_addresses_flag:
            val = 'exclude_contracts ' + val
        if exclude_below_fees_flag:
            val = 'exclude_below_fees ' + val
        if top_limit_value > 0:
            val = f'top-{top_limit_value}_{top_limit_type} ' + val
        csv_row.append(metrics[val])
    return csv_row


def write_csv_output(output_rows):
    header = ['ledger', 'snapshot date', 'no_clustering', 'exclude_contract_addresses', 'top_limit_type', 'top_limit_value']
    header += hlp.get_metrics()

    no_clustering = hlp.get_no_clustering_flag()
    exclude_contract_addresses_flag = hlp.get_exclude_contracts_flag()
    top_limit_type = hlp.get_top_limit_type()
    top_limit_value = hlp.get_top_limit_value()
    output_filename = 'output'
    if no_clustering:
        output_filename += '-no_clustering'
    if exclude_contract_addresses_flag:
        output_filename += '-exclude_contract_addresses'
    if top_limit_value:
        output_filename += f'-{top_limit_type}_{top_limit_value}'
    output_filename += '.csv'

    output_dir = hlp.get_output_directories()[0]
    with open(output_dir / output_filename, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(header)
        csv_writer.writerows(output_rows)


def analyze(ledgers, snapshot_dates):
    output_rows = []
    for ledger in ledgers:
        for date in snapshot_dates:
            logging.info(f'[*] {ledger} - {date}')

            db_paths = [db_dir / f'{ledger}_{date}.db' for db_dir in hlp.get_output_directories()]
            db_file = False
            for filename in db_paths:
                if os.path.isfile(filename):
                    db_file = filename
                    break
            if not db_file:
                logging.error('Snapshot db does not exist')
                continue

            conn = get_connector(db_file)
            metrics_values = analyze_snapshot(conn, ledger, date)
            output_rows.append(get_output_row(ledger, date, metrics_values))
            for metric, value in metrics_values.items():
                logging.info(f'{metric}: {value}')

    write_csv_output(output_rows)
    return output_rows
