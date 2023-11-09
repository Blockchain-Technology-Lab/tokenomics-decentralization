from tokenomics_decentralization.schema import get_connector
from tokenomics_decentralization.helper import INPUT_DIR, MAPPING_INFO_DIR
import os
import sqlite3
import json
import csv
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def fill_db_with_addresses(conn, ledger):
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO ledgers(name) VALUES (?)", (ledger, ))
        conn.commit()
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            pass
        else:
            raise e

    ledger_id = cursor.execute("SELECT id FROM ledgers WHERE name=?", (ledger, )).fetchone()[0]

    try:
        with open(MAPPING_INFO_DIR / f'addresses/{ledger}.json') as f:
            address_entities = json.load(f)
            for addr, info in address_entities.items():
                entity = info['name']
                try:
                    cursor.execute("INSERT INTO entities(name, ledger_id) VALUES (?, ?)", (entity, ledger_id))
                    conn.commit()
                except sqlite3.IntegrityError as e:
                    if 'UNIQUE constraint failed' in str(e):
                        pass
                    else:
                        raise e

                entity_id = cursor.execute("SELECT id FROM entities WHERE name=? AND ledger_id=?", (entity, ledger_id)).fetchone()[0]

                try:
                    cursor.execute("INSERT INTO addresses(name, ledger_id, entity_id) VALUES (?, ?, ?)", (addr, ledger_id, entity_id))
                except sqlite3.IntegrityError as e:
                    if 'UNIQUE constraint failed' in str(e):
                        cursor.execute("UPDATE addresses SET entity_id=? WHERE name=? AND ledger_id=?", (entity_id, addr, ledger_id))
                    else:
                        raise e

                if 'is_contract' in info.keys() and info['is_contract']:
                    cursor.execute("UPDATE addresses SET is_contract=? WHERE name=? AND ledger_id=?", (info['is_contract'], addr, ledger_id))
        conn.commit()
    except FileNotFoundError:
        return


def fill_db_with_balances(conn, ledger, snapshot):
    cursor = conn.cursor()

    ledger_id = cursor.execute("SELECT id FROM ledgers WHERE name=?", (ledger, )).fetchone()[0]

    input_file = INPUT_DIR / f'{ledger}_{snapshot}_raw_data.csv'
    if os.path.isfile(input_file):
        with open(input_file) as f:
            csv_reader = csv.reader(f, delimiter=',')
            try:
                cursor.execute("INSERT INTO snapshots(name, ledger_id) VALUES (?, ?)", (snapshot, ledger_id))
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    pass
                else:
                    raise e

            snapshot_id = cursor.execute("SELECT id FROM snapshots WHERE ledger_id=? AND name=?", (ledger_id, snapshot)).fetchone()[0]

            circulation = 0
            next(csv_reader, None)  # skip header
            for line in csv_reader:
                address, balance = line[0], int(line[-1])

                # For Ethereum, store the balance in Gwei
                if ledger == 'ethereum':
                    balance /= int(10**9)

                circulation += balance

                try:
                    cursor.execute("INSERT INTO addresses(name, ledger_id) VALUES (?, ?)", (address, ledger_id))
                except sqlite3.IntegrityError as e:
                    if 'UNIQUE constraint failed' in str(e):
                        pass
                    else:
                        raise e

                address_id = cursor.execute("SELECT id FROM addresses WHERE ledger_id=? AND name=?", (ledger_id, address)).fetchone()[0]
                try:
                    cursor.execute("INSERT INTO balances(balance, snapshot_id, address_id) VALUES (?, ?, ?)", (balance, snapshot_id, address_id))
                except sqlite3.IntegrityError as e:
                    if 'UNIQUE constraint failed' in str(e):
                        pass
                    else:
                        raise e

            cursor.execute("UPDATE snapshots SET circulation=? WHERE id=?", (str(circulation), snapshot_id))

            conn.commit()


def apply_mapping(ledger, snapshot, db_directories, force_map_addresses, force_map_balances):
    logging.info(f'Mapping {ledger} {snapshot}')
    input_filename = INPUT_DIR / f'{ledger}_{snapshot}_raw_data.csv'
    db_paths = [db_dir / f'{ledger}_{snapshot}.db' for db_dir in db_directories]
    db_file = False
    for filename in db_paths:
        if os.path.isfile(filename):
            db_file = filename
            break
    if not db_file and os.path.isfile(input_filename):
        db_file = db_paths[0]
        force_map_addresses = True
        force_map_balances = True

    if db_file:
        conn = get_connector(db_file)

        if force_map_addresses:
            logging.info('Mapping addresses')
            fill_db_with_addresses(conn, ledger)

        if force_map_balances:
            logging.info('Mapping balances')
            fill_db_with_balances(conn, ledger, snapshot)

        logging.info('Finished')
    else:
        logging.info('Both input and db files do not exist')
