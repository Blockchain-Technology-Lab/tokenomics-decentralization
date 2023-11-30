from tokenomics_decentralization.schema import get_connector
import tokenomics_decentralization.helper as hlp
import tokenomics_decentralization.db_helper as db_hlp
import os
import json
import csv
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def fill_db_with_addresses(conn, ledger):
    db_hlp.insert_ledger(conn, ledger)

    try:
        with open(hlp.MAPPING_INFO_DIR / f'addresses/{ledger}.json') as f:
            address_entities = json.load(f)
            for addr, info in address_entities.items():
                entity = info['name']
                db_hlp.insert_entity(conn, ledger, entity)
                is_contract = 'is_contract' in info.keys() and info['is_contract']

                db_hlp.insert_update_address(conn, ledger, addr, entity, is_contract)
        db_hlp.commit_database()
    except FileNotFoundError:
        return


def fill_db_with_balances(conn, ledger, snapshot):
    input_paths = [input_dir / f'{ledger}_{snapshot}_raw_data.csv' for input_dir in hlp.get_input_directories()]
    for input_filename in input_paths:
        if os.path.isfile(input_filename):
            with open(input_filename) as f:
                csv_reader = csv.reader(f, delimiter=',')
                db_hlp.insert_snapshot(conn, ledger, snapshot)

                circulation = 0
                next(csv_reader, None)  # skip header
                for line in csv_reader:
                    address, balance = line[0], int(line[-1])

                    # For Ethereum, store the balance in Gwei
                    if ledger == 'ethereum':
                        balance /= int(10**9)

                    if balance == 0:
                        continue

                    circulation += balance
                    db_hlp.insert_address_without_update(conn, ledger, address)
                    db_hlp.insert_balance(conn, ledger, snapshot, address, balance)

                db_hlp.update_circulation(conn, ledger, snapshot, circulation)
                db_hlp.commit_database()
            return


def apply_mapping(ledger, snapshot):
    force_map_addresses = hlp.get_force_map_addresses_flag()
    force_map_balances = hlp.get_force_map_balances_flag()

    logging.info(f'Mapping {ledger} {snapshot}')
    db_paths = [db_dir / f'{ledger}_{snapshot}.db' for db_dir in hlp.get_output_directories()]
    db_file = False
    for filename in db_paths:
        if os.path.isfile(filename):
            db_file = filename
            break
    if not db_file:
        input_paths = [input_dir / f'{ledger}_{snapshot}_raw_data.csv' for input_dir in hlp.get_input_directories()]
        for input_filename in input_paths:
            if os.path.isfile(input_filename):
                db_file = db_paths[0]
                force_map_addresses = True
                force_map_balances = True
                break

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
        logging.info('Neither input nor db files exist')
