import tokenomics_decentralization.helper as hlp
import tokenomics_decentralization.db_helper as db_hlp
import os
import json
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def apply_mapping(ledger):
    force_map_addresses = hlp.get_force_map_addresses_flag()
    db_filename = db_hlp.get_db_filename(ledger)
    if not os.path.isfile(db_filename) or force_map_addresses:
        logging.info(f'Mapping {ledger} addresses')

        conn = db_hlp.get_connector(db_filename)
        clusters = hlp.get_clusters(ledger)
        logging.info(f'Collected {ledger} clusters')
        with open(hlp.MAPPING_INFO_DIR / f'addresses/{ledger}.jsonl') as f:
            for line in f:
                info = json.loads(line)
                source = info['source']
                if source in hlp.get_active_sources():
                    address = info['address']
                    entity = info['name']
                    if entity in clusters.keys():
                        entity = clusters[entity]
                    is_contract = 'is_contract' in info.keys() and info['is_contract']
                    db_hlp.insert_mapping(conn, address, entity, is_contract)
        db_hlp.commit_database(conn)

        logging.info('Finished mapping db')
