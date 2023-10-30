from tokenomics_decentralization.schema import get_connector
import os
import sqlite3
import json
import csv
import pathlib
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
RAW_DATA_PATH = ROOT_DIR / 'input'
MAPPING_INFO_PATH = ROOT_DIR / 'mapping_information'


def fill_db_with_addresses(conn, ledger):
    cursor = conn.cursor()

    try:
        cursor.execute(f"INSERT INTO ledgers(name) VALUES ('{ledger}')")
        conn.commit()
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            pass
        else:
            raise e

    ledger_id = cursor.execute(f"SELECT id FROM ledgers WHERE name='{ledger}'").fetchone()[0]

    with open(MAPPING_INFO_PATH / f'addresses/{ledger}.json') as f:
        address_entities = json.load(f)
        for addr, info in address_entities.items():
            entity = info['name']
            try:
                cursor.execute(f"INSERT INTO entities(name, ledger_id) VALUES ('{entity}', {ledger_id})")
                conn.commit()
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    pass
                else:
                    raise e

            entity_id = cursor.execute(f"SELECT id FROM entities WHERE name='{entity}' AND ledger_id={ledger_id}").fetchone()[0]

            try:
                cursor.execute(f"INSERT INTO addresses(name, ledger_id, entity_id) VALUES ('{addr}', {ledger_id}, {entity_id})")
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    old_entity = cursor.execute(f"SELECT entity_id FROM addresses WHERE name='{addr}' AND ledger_id={ledger_id}").fetchone()[0]
                    if old_entity is None:
                        cursor.execute(f"UPDATE addresses SET entity_id={entity_id} WHERE name='{addr}' AND ledger_id={ledger_id}")
                else:
                    raise e
    conn.commit()


def fill_db_with_balances(conn, ledger, snapshot):
    cursor = conn.cursor()

    ledger_id = cursor.execute(f"SELECT id FROM ledgers WHERE name='{ledger}'").fetchone()[0]

    input_file = RAW_DATA_PATH / f'{ledger}_{snapshot}_raw_data.csv'
    if os.path.isfile(input_file):
        with open(input_file) as f:
            csv_reader = csv.reader(f, delimiter=',')
            try:
                cursor.execute(f"INSERT INTO snapshots(name, ledger_id) VALUES ('{snapshot}', {ledger_id})")
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    pass
                else:
                    raise e

            snapshot_id = cursor.execute(f"SELECT id FROM snapshots WHERE ledger_id={ledger_id} AND name='{snapshot}'").fetchone()[0]

            circulation = 0
            for line in csv_reader:
                if 'address' in line:
                    continue

                address, balance = line[0], int(line[-1])
                circulation += balance

                try:
                    cursor.execute(f"INSERT INTO addresses(name, ledger_id) VALUES ('{address}', {ledger_id})")
                except sqlite3.IntegrityError as e:
                    if 'UNIQUE constraint failed' in str(e):
                        pass
                    else:
                        raise e

                address_id = cursor.execute(f"SELECT id FROM addresses WHERE ledger_id={ledger_id} AND name='{address}'").fetchone()[0]
                try:
                    cursor.execute(f"INSERT INTO balances(balance, snapshot_id, address_id) VALUES ({balance}, {snapshot_id}, {address_id})")
                except sqlite3.IntegrityError as e:
                    if 'UNIQUE constraint failed' in str(e):
                        prev_balance = int(cursor.execute(f"SELECT balance FROM balances WHERE address_id={address_id} AND snapshot_id={snapshot_id}").fetchone()[0])
                        cursor.execute(f"UPDATE balances SET balance={prev_balance+balance} WHERE address_id={address_id} AND snapshot_id={snapshot_id}")
                    else:
                        raise e

            cursor.execute(f"UPDATE snapshots SET circulation={circulation} WHERE id={snapshot_id}")

            conn.commit()


def apply_mapping(ledger, snapshot, db_directories):
    input_filename = RAW_DATA_PATH / f'{ledger}_{snapshot}_raw_data.csv'
    db_paths = [db_dir / f'{ledger}_{snapshot}.db' for db_dir in db_directories]
    db_file = False
    for filename in db_paths:
        if os.path.isfile(filename):
            db_file = filename
            break
    if not db_file and os.path.isfile(input_filename):
        db_file = db_paths[0]

    if db_file:
        conn = get_connector(db_file)

        logging.info('Mapping addresses')
        fill_db_with_addresses(conn, ledger)

        logging.info('Mapping balances')
        fill_db_with_balances(conn, ledger, snapshot)

        logging.info('Finished')
    else:
        logging.info('Snapshot input or db file does not exist')
