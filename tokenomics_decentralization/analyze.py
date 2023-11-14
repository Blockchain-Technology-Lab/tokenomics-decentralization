from tokenomics_decentralization.schema import get_connector
from tokenomics_decentralization.metrics import compute_hhi, compute_tau, compute_gini, compute_shannon_entropy, compute_total_entities
import tokenomics_decentralization.helper as hlp
from time import time
import sqlite3
import os
import logging
import csv

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def get_non_clustered_balance_entries(cursor, snapshot_id):
    exclude_contract_addresses = 'AND addresses.is_contract=0' if hlp.get_exclude_contracts_flag() else ''

    start = time()
    query = f'''
        SELECT addresses.name, balance
        FROM balances
        LEFT JOIN addresses ON balances.address_id=addresses.id
        WHERE snapshot_id=?
        {exclude_contract_addresses}
        ORDER BY balance DESC
    '''

    entries = cursor.execute(query, (snapshot_id, )).fetchall()
    logging.info(f'Retrieving entries took about {time() - start} seconds')

    return entries


def get_balance_entries(cursor, snapshot_id):
    exclude_contract_addresses = 'AND addresses.is_contract=0' if hlp.get_exclude_contracts_flag() else ''

    start = time()
    query = f'''
        SELECT IFNULL(entities.name, addresses.name) AS entity, SUM(CAST(balance AS REAL)) AS aggregate_balance
        FROM balances
        LEFT JOIN addresses ON balances.address_id=addresses.id
        LEFT JOIN entities ON addresses.entity_id=entities.id
        WHERE snapshot_id=?
        {exclude_contract_addresses}
        GROUP BY entity
        ORDER BY aggregate_balance DESC
    '''

    entries = cursor.execute(query, (snapshot_id, )).fetchall()
    logging.info(f'Retrieving entries took about {time() - start} seconds')

    return entries


def analyze_snapshot(conn, ledger, snapshot):
    force_analyze = hlp.get_force_analyze_flag()
    no_clustering = hlp.get_no_clustering_flag()
    exclude_contract_addresses_flag = hlp.get_exclude_contracts_flag()
    top_limit_type = hlp.get_top_limit_type()
    top_limit_value = hlp.get_top_limit_value()

    cursor = conn.cursor()

    ledger_id = cursor.execute("SELECT id FROM ledgers WHERE name=?", (ledger, )).fetchone()[0]

    snapshot_info = cursor.execute("SELECT * FROM snapshots WHERE name=? AND ledger_id=?", (snapshot, ledger_id)).fetchone()
    snapshot_id = snapshot_info[0]
    circulation = int(float(snapshot_info[3]))

    compute_functions = {
        'hhi': compute_hhi,
        'shannon entropy': compute_shannon_entropy,
        'gini': compute_gini,
        'total entities': compute_total_entities,
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
        if top_limit_value > 0:
            flagged_metric = f'top-{top_limit_value}_{top_limit_type} ' + flagged_metric

        val = cursor.execute('SELECT value FROM metrics WHERE snapshot_id=? and name=?', (snapshot_id, flagged_metric)).fetchone()
        if val and not force_analyze:
            metric_value = val[0]
        else:
            if not entries:
                if no_clustering:
                    entries = get_non_clustered_balance_entries(cursor, snapshot_id)
                else:
                    entries = get_balance_entries(cursor, snapshot_id)

                if top_limit_type == 'percentage':
                    total_entities = compute_functions['total entities'](entries, circulation)
                    top_limit_percentage_value = int(total_entities * top_limit_value)
                    entries = entries[:top_limit_percentage_value]
                elif top_limit_type == 'absolute' and top_limit_value > 0:
                    entries = entries[:top_limit_value]

                if top_limit_value > 0:
                    circulation = hlp.get_circulation_from_entries(entries)

            logging.info(f'Computing {flagged_metric}')
            if 'tau' in default_metric_name:
                threshold = float(default_metric_name.split('=')[1])
                metric_value = compute_functions[default_metric_name](entries, circulation, threshold)[0]
            else:
                metric_value = compute_functions[default_metric_name](entries, circulation)

            try:
                cursor.execute("INSERT INTO metrics(name, value, snapshot_id) VALUES (?, ?, ?)", (flagged_metric, metric_value, snapshot_id))
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    cursor.execute("UPDATE metrics SET value=? WHERE name=? AND snapshot_id=?", (metric_value, flagged_metric, snapshot_id))
                else:
                    raise e

            conn.commit()

        if any(['tau' in default_metric_name, 'total entities' in default_metric_name]):
            metric_value = int(metric_value)

        metrics_results[flagged_metric] = metric_value

    return metrics_results


def get_output_row(ledger, date, metrics):
    no_clustering = hlp.get_no_clustering_flag()
    exclude_contract_addresses_flag = hlp.get_exclude_contracts_flag()
    top_limit_type = hlp.get_top_limit_type()
    top_limit_value = hlp.get_top_limit_value()

    csv_row = [ledger, date, no_clustering, exclude_contract_addresses_flag, top_limit_type, top_limit_value]

    for metric_name in hlp.get_metrics():
        val = metric_name
        if no_clustering:
            val = 'non-clustered ' + val
        if exclude_contract_addresses_flag:
            val = 'exclude_contracts ' + val
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
