from tokenomics_decentralization.schema import get_connector
from tokenomics_decentralization.metrics import compute_hhi, compute_tau, compute_gini, compute_shannon_entropy
from time import time
import sqlite3
import os
import pathlib
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

TAU_THRESHOLDS = [0.33, 0.5, 0.66]
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent


def get_non_clustered_balance_entries(cursor, ledger_id, snapshot_id):
    start = time()
    query = f'''
        SELECT addresses.name, balance
        FROM balances
        LEFT JOIN addresses ON balances.address_id=addresses.id
        WHERE snapshot_id={snapshot_id}
        ORDER BY balance DESC
    '''

    entries = cursor.execute(query).fetchall()
    logging.info(f'Retrieving entries took about {time() - start} seconds')

    return entries


def get_balance_entries(cursor, ledger_id, snapshot_id):
    start = time()
    query = f'''
        SELECT IFNULL(entities.name, addresses.name) AS entity, SUM(CAST(balance AS REAL)) AS aggregate_balance
        FROM balances
        LEFT JOIN addresses ON balances.address_id=addresses.id
        LEFT JOIN entities ON addresses.entity_id=entities.id
        WHERE snapshot_id={snapshot_id}
        GROUP BY entity
        ORDER BY aggregate_balance DESC
    '''

    entries = cursor.execute(query).fetchall()
    logging.info(f'Retrieving entries took about {time() - start} seconds')

    return entries


def analyze_snapshot(conn, ledger, snapshot, force_compute, no_clustering):
    cursor = conn.cursor()

    ledger_id = cursor.execute(f"SELECT id FROM ledgers WHERE name='{ledger}'").fetchone()[0]

    snapshot_info = cursor.execute(f"SELECT * FROM snapshots WHERE name='{snapshot}' AND ledger_id={ledger_id}").fetchone()
    snapshot_id = snapshot_info[0]
    circulation = int(snapshot_info[3])

    compute_functions = {
        'hhi': compute_hhi,
        'shannon entropy': compute_shannon_entropy,
        'gini': compute_gini
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

        logging.info(f'Computing {metric_name}')

        val = cursor.execute(f'SELECT value FROM metrics WHERE snapshot_id={snapshot_id} and name="{metric_name}"').fetchone()
        if val and not force_compute:
            metric_value = val[0]
        else:
            if not entries:
                if no_clustering:
                    entries = get_non_clustered_balance_entries(cursor, ledger_id, snapshot_id)
                else:
                    entries = get_balance_entries(cursor, ledger_id, snapshot_id)

            if 'tau' in metric_name:
                threshold = float(metric_name.split('=')[1])
                metric_value = compute_tau(entries, circulation, threshold)[0]
            else:
                metric_value = compute_functions[metric_name](entries, circulation)

            try:
                cursor.execute(f"INSERT INTO metrics(name, value, snapshot_id) VALUES ('{metric_name}', {metric_value}, {snapshot_id})")
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    cursor.execute(f"UPDATE metrics SET value={metric_value} WHERE name='{metric_name}' AND snapshot_id={snapshot_id}")
                else:
                    raise e

            conn.commit()

        if 'tau' in metric_name:
            metric_value = int(metric_value)

        metrics_results[metric_name] = metric_value

    return metrics_results


def get_output(ledger, year, metrics, no_clustering):
    if no_clustering:
        csv_output = f'{ledger},{year},{metrics["non-clustered gini"]},{metrics["non-clustered hhi"]},{metrics["non-clustered shannon entropy"]}'
    else:
        csv_output = f'{ledger},{year},{metrics["gini"]},{metrics["hhi"]},{metrics["shannon entropy"]}'

    for tau in TAU_THRESHOLDS:
        if no_clustering:
            value = metrics[f'non-clustered tau={tau}']
        else:
            value = metrics[f'tau={tau}']
        csv_output += f',{value}'

    return csv_output


def write_csv_output(output):
    csv_output = ['ledger,snapshot,gini,hhi,shannon entropy']
    for tau in TAU_THRESHOLDS:
        csv_output[-1] += f',tau={tau}'

    csv_output += output

    with open('output.csv', 'w') as f:
        f.write('\n'.join(csv_output))


def analyze(ledgers, snapshots, force_compute, db_directories, no_clustering):
    output = []
    for ledger in ledgers:
        for snapshot in snapshots:
            year = snapshot[:4]
            logging.info(f'[*] {ledger} - {year}')

            db_paths = [db_dir / f'{ledger}_{snapshot}.db' for db_dir in db_directories]
            db_file = False
            for filename in db_paths:
                if os.path.isfile(filename):
                    db_file = filename
                    break
            if not db_file:
                logging.error('Snapshot db does not exist')
                continue

            conn = get_connector(db_file)
            metrics_values = analyze_snapshot(conn, ledger, snapshot, force_compute, no_clustering)
            output.append(get_output(ledger, year, metrics_values, no_clustering))
            for metric, value in metrics_values.items():
                logging.info(f'{metric}: {value}')

    write_csv_output(output)
