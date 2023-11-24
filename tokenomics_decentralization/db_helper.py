import sqlite3
import tokenomics_decentralization.helper as hlp
from time import time
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def commit_database(conn):
    conn.commit()


def get_ledger_id(conn, ledger):
    cursor = conn.cursor()
    return cursor.execute("SELECT id FROM ledgers WHERE name=?", (ledger, )).fetchone()[0]


def get_snapshot_info(conn, ledger, snapshot):
    cursor = conn.cursor()
    ledger_id = cursor.execute("SELECT id FROM ledgers WHERE name=?", (ledger, )).fetchone()[0]
    snapshot_info = cursor.execute("SELECT * FROM snapshots WHERE name=? AND ledger_id=?", (snapshot, ledger_id)).fetchone()
    return snapshot_info


def get_metric_value(conn, ledger, snapshot, metric):
    cursor = conn.cursor()
    ledger_id = cursor.execute("SELECT id FROM ledgers WHERE name=?", (ledger, )).fetchone()[0]
    snapshot_id = cursor.execute("SELECT id FROM snapshots WHERE name=? AND ledger_id=?", (snapshot, ledger_id)).fetchone()[0]
    val = cursor.execute('SELECT value FROM metrics WHERE snapshot_id=? and name=?', (snapshot_id, metric)).fetchone()
    return val


def insert_metric(conn, ledger, snapshot, metric_name, metric_value):
    cursor = conn.cursor()
    ledger_id = cursor.execute("SELECT id FROM ledgers WHERE name=?", (ledger, )).fetchone()[0]
    snapshot_id = cursor.execute("SELECT id FROM snapshots WHERE name=? AND ledger_id=?", (snapshot, ledger_id)).fetchone()[0]

    try:
        cursor.execute("INSERT INTO metrics(name, value, snapshot_id) VALUES (?, ?, ?)", (metric_name, metric_value, snapshot_id))
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            cursor.execute("UPDATE metrics SET value=? WHERE name=? AND snapshot_id=?", (metric_value, metric_name, snapshot_id))
        else:
            raise e


def get_non_clustered_balance_entries(conn, snapshot_id, ledger, balance_threshold):
    cursor = conn.cursor()

    exclude_contract_addresses_clause = 'AND addresses.is_contract=0' if hlp.get_exclude_contracts_flag() else ''
    exclude_below_threshold_clause = f'AND balance >= {balance_threshold}' if balance_threshold >= 0 else ''
    special_addresses = hlp.get_special_addresses(ledger)
    if len(special_addresses) == 0:
        special_addresses_clause = ''
    elif len(special_addresses) == 1:
        special_addresses_clause = f'AND addresses.name NOT IN ("{special_addresses[0]}")'
    else:
        special_addresses_clause = f'AND addresses.name NOT IN {tuple(special_addresses)}'

    start = time()
    query = f'''
        SELECT addresses.name, balance
        FROM balances
        LEFT JOIN addresses ON balances.address_id=addresses.id
        WHERE snapshot_id=?
        {exclude_below_threshold_clause}
        {exclude_contract_addresses_clause}
        {special_addresses_clause}
        ORDER BY balance DESC
    '''

    entries = cursor.execute(query, (snapshot_id, )).fetchall()
    logging.info(f'Retrieving entries took about {time() - start} seconds')

    return entries


def get_balance_entries(conn, snapshot_id, ledger, balance_threshold):
    cursor = conn.cursor()

    exclude_contract_addresses_clause = 'AND addresses.is_contract=0' if hlp.get_exclude_contracts_flag() else ''
    exclude_below_threshold_clause = f'AND balance >= {balance_threshold}' if balance_threshold >= 0 else ''
    special_addresses = hlp.get_special_addresses(ledger)
    if len(special_addresses) == 0:
        special_addresses_clause = ''
    elif len(special_addresses) == 1:
        special_addresses_clause = f'AND addresses.name NOT IN ("{special_addresses[0]}")'
    else:
        special_addresses_clause = f'AND addresses.name NOT IN {tuple(special_addresses)}'

    start = time()
    query = f'''
        SELECT IFNULL(entities.name, addresses.name) AS entity, SUM(CAST(balance AS REAL)) AS aggregate_balance
        FROM balances
        LEFT JOIN addresses ON balances.address_id=addresses.id
        LEFT JOIN entities ON addresses.entity_id=entities.id
        WHERE snapshot_id=?
        {exclude_below_threshold_clause}
        {exclude_contract_addresses_clause}
        {special_addresses_clause}
        GROUP BY entity
        ORDER BY aggregate_balance DESC
    '''

    entries = cursor.execute(query, (snapshot_id, )).fetchall()
    logging.info(f'Retrieving entries took about {time() - start} seconds')

    return entries
