from tokenomics_decentralization.schema import get_connector
from tokenomics_decentralization.metrics import compute_hhi, compute_tau, compute_gini, compute_shannon_entropy, compute_total_entities
import tokenomics_decentralization.helper as hlp
from time import time
import sqlite3
import os
import logging
import csv

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

TAU_THRESHOLDS = [0.33, 0.5, 0.66]


def get_non_clustered_balance_entries(cursor, snapshot_id):
    start = time()
    query = '''
        SELECT addresses.name, balance
        FROM balances
        LEFT JOIN addresses ON balances.address_id=addresses.id
        WHERE snapshot_id=?
        ORDER BY balance DESC
    '''

    entries = cursor.execute(query, (snapshot_id, )).fetchall()
    logging.info(f'Retrieving entries took about {time() - start} seconds')

    return entries


def get_balance_entries(cursor, snapshot_id):
    start = time()
    query = '''
        SELECT IFNULL(entities.name, addresses.name) AS entity, SUM(CAST(balance AS REAL)) AS aggregate_balance
        FROM balances
        LEFT JOIN addresses ON balances.address_id=addresses.id
        LEFT JOIN entities ON addresses.entity_id=entities.id
        WHERE snapshot_id=?
        GROUP BY entity
        ORDER BY aggregate_balance DESC
    '''

    entries = cursor.execute(query, (snapshot_id, )).fetchall()
    logging.info(f'Retrieving entries took about {time() - start} seconds')

    return entries


def analyze_snapshot(conn, ledger, snapshot, force_compute, no_clustering):
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
    for threshold in TAU_THRESHOLDS:
        compute_functions[f'tau={threshold}'] = compute_tau

    metric_names = list(compute_functions.keys())
    for key in metric_names:
        compute_functions['non-clustered ' + key] = compute_functions[key]

    entries = None
    metrics_results = {}
    for metric_name in metric_names:
        if no_clustering:
            metric_name = 'non-clustered ' + metric_name

        val = cursor.execute('SELECT value FROM metrics WHERE snapshot_id=? and name=?', (snapshot_id, metric_name)).fetchone()
        if val and not force_compute:
            metric_value = val[0]
        else:
            if not entries:
                if no_clustering:
                    entries = get_non_clustered_balance_entries(cursor, snapshot_id)
                else:
                    entries = get_balance_entries(cursor, snapshot_id)

            logging.info(f'Computing {metric_name}')
            if 'tau' in metric_name:
                threshold = float(metric_name.split('=')[1])
                metric_value, _ = compute_tau(entries, circulation, threshold)
            else:
                metric_value = compute_functions[metric_name](entries, circulation)

            try:
                cursor.execute("INSERT INTO metrics(name, value, snapshot_id) VALUES (?, ?, ?)", (metric_name, metric_value, snapshot_id))
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    cursor.execute("UPDATE metrics SET value=? WHERE name=? AND snapshot_id=?", (metric_value, metric_name, snapshot_id))
                else:
                    raise e

            conn.commit()

        if 'tau' in metric_name or metric_name == 'total entities':
            metric_value = int(metric_value)

        metrics_results[metric_name] = metric_value

    return metrics_results


def get_output_row(ledger, year, metrics, no_clustering):
    csv_row = []
    if no_clustering:
        csv_row.extend([ledger, year, metrics["non-clustered total entities"], metrics["non-clustered gini"], metrics["non-clustered hhi"], metrics["non-clustered shannon entropy"]])
    else:
        csv_row.extend([ledger, year, metrics["total entities"], metrics["gini"], metrics["hhi"], metrics["shannon entropy"]])

    for tau in TAU_THRESHOLDS:
        if no_clustering:
            csv_row.append(metrics[f'non-clustered tau={tau}'])
        else:
            csv_row.append(metrics[f'tau={tau}'])

    return csv_row


def write_csv_output(output_rows):
    header = ['ledger', 'snapshot date', 'total entities', 'gini', 'hhi', 'shannon entropy']
    header.extend([f'tau={tau}' for tau in TAU_THRESHOLDS])

    with open(hlp.OUTPUT_DIR / 'output.csv', 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(header)
        csv_writer.writerows(output_rows)


def analyze(ledgers, snapshot_dates, force_compute, db_directories, no_clustering):
    output_rows = []
    for ledger in ledgers:
        for date in snapshot_dates:
            logging.info(f'[*] {ledger} - {date}')

            db_paths = [db_dir / f'{ledger}_{date}.db' for db_dir in db_directories]
            db_file = False
            for filename in db_paths:
                if os.path.isfile(filename):
                    db_file = filename
                    break
            if not db_file:
                logging.error('Snapshot db does not exist')
                continue

            conn = get_connector(db_file)
            metrics_values = analyze_snapshot(conn, ledger, date, force_compute, no_clustering)
            output_rows.append(get_output_row(ledger, date, metrics_values, no_clustering))
            for metric, value in metrics_values.items():
                logging.info(f'{metric}: {value}')

    write_csv_output(output_rows)
    return output_rows
